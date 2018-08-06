#!/usr/bin/perl

# PSLS TS display

use strict;
use warnings;
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


# banner
printf "----------------------------------------\n";
printf "NTS   0 0 0 0  0 0 0 0  0 1 1 1  1 1 1 1\n";
printf "      1 2 3 4  5 6 7 8  9 0 1 2  3 4 5 6\n";
printf "----------------------------------------\n";

# read register 0 to 9 and print it on stdout
my $words = $m->read_holding_registers(20610, 20);
if ($words) 
{
  my $terme = 0;
  
  foreach my $word (@$words) 
  {
    my @bits = reverse (split ("", unpack ("b*", pack ("S", $word))));
    
    if ($terme == 0) 
    {
      printf "ME    ";
      $terme++;
    } else
    {
      printf "T%02d   ", $terme++;
    }
    
    my $by4 = 0;
    foreach my $bit (@bits) 
    {
      if ($bit)
      { 
        printf "%1b ", $bit;
      }
      else
      {
        printf ". ";
      }
      printf " " if ! (++$by4 % 4);
    }
    printf "\n";
  }
  printf "\n";
}
