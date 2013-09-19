#!/usr/bin/perl -w

# PSLS TM display

use strict;
use MBclient;

# create modbus object
my $m = MBclient->new();

# on local modbus server
$m->host("127.0.0.1");
$m->unit_id(1);

# open TCP socket
if (! $m->open()) {
  print "unable to open TCP socket.\n";
  exit(1);
} 

# read register 0 to 9 and print it on stdout
my $words = $m->read_holding_registers(20650, 30);
if ($words) 
{
  my $terme = 40;
  
  foreach my $word (@$words) 
  {
    printf "T%02d   %d\n", $terme++, $word;
  }
  printf "\n";
}
