#! /usr/bin/perl

use strict;
use warnings;
use YAML::Tiny;

my %answer_readers = (
                     "MC" => \&read_MC_ans
                    ,"MA" => \&read_MA_ans
                    ,"ORD" => \&read_ORD_ans
                    ,"NUM" => \&read_NUM_ans
                    );

my %YAML_writers = (
                 "MC" => \&write_MC_YAML
                 ,"MA" => \&write_MA_YAML
                 ,"ORD" => \&write_ORD_YAML
                 ,"NUM" => \&write_NUM_YAML
                 );



# 
# main loop. reads text file and generates blackboard formatted file for each argument
# 
for my $infile (@ARGV)
{
  # generate an output filename from the input filename
  # we just strip off the file's extension and replace it with .yaml
	my $outfile = $infile;
	$outfile =~ s/(\.\S+)$/.yaml/;
	print "importing Clark formatted questions from $infile and writing YAML formatted questions to $outfile";
	print "WARNING: questions CANNOT have linebreaks. make sure you text editor did not linewrap any questions";


  # read entire file into a sigle string
  # newline characters will be in the string
	open IN, '<', $infile or die "could not open $infile";
	my $text = join '', <IN>;
	close IN;

  # clean up the string.
  #  - replace all tabs with a space
  #  - replace multiple spaces with a single space
  #  - remove any space at the beginning and end of a line
  #  - remove any spaces from blank lines
  #  - replace two or more newline characters with two (this will be used to separate questions)
	$text =~ s/\t/ /g;
	$text =~ s/ +/ /g;
	$text =~ s/^\s*//g;
	$text =~ s/\s*$//g;
	$text =~ s/^\s*//g;
	$text =~ s/\n\s*$//g;
	$text =~ s/ *\n */\n/g;
	$text =~ s/\n\s*\n/\n\n/g;
	$text =~ s/\n\n\n*/\n\n/g;

  # split text into questions.
  # questions are sparated by one or more blank lines
	my @records = split /\n\s*\n/, $text;

	my @questions;

	for my $record (@records)
	{
    # split record into type, question text, and answer
    # WARNING!!! this uses a newline character. questions with line breaks (perhaps from the text editor automatically wrapping them)
    # will cause the answer to be DROPPED
		my @fields = split /\n/, $record;
		chomp @fields;
		my $type = shift @fields;
		my $text = shift @fields;
		my $ans_text = join ":", @fields;

		# stip off any "Type:" tag
		$type =~ s/[Tt]ype[:]//g;
		$type =~ s/\s//g;

		# strip of any question numbers
		$text =~ s/^[0-9]+[\.\)]\s*//;

		my $ans = $answer_readers{$type}->($ans_text);

		push @questions, {"type" => $type, "text" => $text, "answer" => $ans };
	}


  my $yaml_questions = ();
	for my $question (@questions)
	{
		push @{$yaml_questions}, $YAML_writers{ $question->{type} }->($question);
	}

  my $doc = { "questions" => $yaml_questions };


  my $yaml = YAML::Tiny->new( $doc );

  $yaml->write( $outfile );

}






sub write_MC_YAML( $ )
{
	return write_MA_YAML(@_);
}

sub write_MA_YAML( $ )
{
	my ($question) = @_;

	my $text = $question->{text};
  my $answers = {};
  my @labels = ('a'
               ,'b'
               ,'c'
               ,'d'
               ,'e'
               ,'e'
               ,'f'
               ,'g'
               ,'h'
               ,'i');
  my ($ans, $lbl);
  for( my $i = 0; $i < @{$question->{"answer"}}; $i++)
	{
    $ans = $question->{"answer"}->[$i];
    $lbl = $labels[$i];
    $answers->{$lbl} = ($ans->{correct} ? "^":"").$ans->{value} ;
	}

  my $result = { "text" => $text, "answer" => $answers };

	return $result;
}

sub write_ORD_YAML( $ )
{
	my ($question) = @_;

	my $text = $question->{text};
  my $answers = ();

	for my $ans (@{$question->{"answer"}})
	{
    push @{$answers}, $ans->{value};
	}

  my $result = { "text" => $text, "answer" => $answers };

	return $result;
}

sub write_NUM_YAML( $ )
{
	my ($question) = @_;
	my $text  = $question->{text};
  my $answer = {"value"      => $question->{answer}->[0]->{value}
               ,"uncertainty"=> $question->{answer}->[0]->{uncertainty} };

  my $result = { "text" => $text, "answer" => $answer };
	return $result;
}
















sub read_MC_ans( $ )
{
	return read_MA_ans( @_ )
}

sub read_MA_ans( $ )
{
	my ($ans_text) = @_;
	my @answers = split /:/, $ans_text;
	my @ret;
	
	for my $answer (@answers)
	{
		my $correct = 0;
		# check if answer is the correct one and stip of indicator
		$correct = 1 if $answer =~ s/^\s*\*\s*// > 0;
		# strip off any numbering
		$answer =~ s/^\s*[a-zA-z0-9][\.\)]\s*//;
		push @ret, {"value" => $answer, "correct" => $correct};
	}
	
	return \@ret;
}

sub read_ORD_ans( $ )
{
	my %ans = ("a" => "ORD" );

	my ($ans_text) = @_;
	my @answers = split /:/, $ans_text;
	my @ret;
	
	for my $answer (@answers)
	{
		# strip off any numbering
		$answer =~ s/^\s*\**[a-zA-z0-9][\.\)]\s*//;
		push @ret, {"value" => $answer};
	}
	
	return \@ret;
	
	return \%ans;
}

sub read_NUM_ans( $ )
{
	my ($ans_text) = @_;
	my @ret;

	# we want to allow the value and uncertainty to be specified on the same line or different lines.
	# so they may or may not have a ':' between them right now.

	# strip off any lettering or space at the beginning
	$ans_text =~ s/^\s*([a-zA-z][\.\)])*\s*//;
	# strip off any space at the end
	$ans_text =~ s/\s*$//;

	# replace any spaces left with a ':'
	$ans_text =~ s/\s/:/g;
	# replace repeaded ':' with a single ':'
	$ans_text =~ s/:+/:/g;

	my ($val,$unc);
	my @tmp = split /:/, $ans_text;
	$val = $tmp[0];
	$unc = $#tmp > 0 ? $tmp[1] : $val * 0.01;
	$val =~ s/\s//g;
	$unc =~ s/\s//g;
	push @ret, {"value" => $val, "uncertainty" => $unc};
	
	return \@ret;
}

sub read_FIB_ans( $ )
{
	my %ans;
	
	return \%ans;
}




