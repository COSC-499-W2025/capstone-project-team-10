use strict;
use warnings;
use vars;
use constant PI => 3.14159;
use LWP::UserAgent;
use JSON;
use DBI;
use Data::Dumper;

my $ua = LWP::UserAgent->new();
print "Hello, Perl!\n";