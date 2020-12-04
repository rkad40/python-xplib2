#perl

use strict;
use lib "C:/Perl/xplib";

my $s = "It is the best of the rest.  Of this, no one can contest.";

# print "---", "\n";
# print "while (\$s =~ /(\w+est)/g)", "\n";
# if ($s =~ /(\w+est)/)
# {
#     print $1, "\n";
# }

# print "---", "\n";
# print "if (\$s =~ /(\w+est)/)", "\n";
# if ($s =~ /(\w+est)/)
# {
#     print $1, "\n";
# }

# print "---", "\n";
# print "if (\$s =~ /(\w+est)/g)", "\n";
# if ($s =~ /(\w+est)/g)
# {
#     print $1, "\n";
# }

# print "---", "\n";
# print "if (\$s =~ /(\w+est)/)", "\n";
# if ($s =~ /(\w+est)/)
# {
#     print $1, "\n";
# }

print "---", "\n";
print "if (\$s =~ s/(\w+est)/xxx/g)", "\n";
print $1, "\n" if $s =~ s/(\w+est)/xxx/g;
print "\$s = \"$s\";\n"



