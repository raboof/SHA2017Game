# SHA2017Game

The [SHA2017](https://sha2017.org/) hacker event in Zeewolde, the Netherlands
was one of the first events to feature an 
[ESP32-based electronic badge](https://wiki.sha2017.org/w/Projects:Badge) for
all participants.

The MicroPython-based firmware for this badge laid the foundation for a badge
platform and accompanying 'app store' under the
[badge.team](https://badge.team) moniker.

## The game

One of the apps available for the badge at the start of the event was this
SHA2017 game.

Every user would be assigned a 'team color' (red/yellow/blue) 'fragment' on
startup, and would be instructed to find other camp visitors with the same
colour to exchange fragements with. Also, it added a small fragment to the
badge 'home screen' to 'flash' the badge LEDs in the users' team colour.

To share fragments, 2 badges had to be 'paired' to each other, after which
they would share (all) their fragments with each other.

After reaching 25 fragments, you would 'win' the game, and your badge would
be awarded access to some code that made your LED flashing 'sparkle'.

## Internals

There were originally intended to be 6 teams. However, because your team was
determined by your badge MAC address, and the ESP32 uses even/odd MAC addresses
for AP/client mode, in practice only 3 teams were actually populated. This
turned out to be the perfect number anyway.

The fragments were shared in true peer-to-peer fashion, by having one badge
act as a WiFi access point and the other connecting to it.

The 'fragments' were keys in a
[Shamir's Secret Sharing](https://github.com/blockstack/secret-sharing) setup -
collecting actually helped you collect enough information to reconstruct the
URL where the 'sparkle' prize code could be collected.

## Results

A 6-minute recap of the project can be found [at media.ccc.de](https://media.ccc.de/v/SHA2017-345-lightning_talks_day_5#t=101). The slides are [here](https://docs.google.com/presentation/d/124f7MaN0OT_VTA1v6g1vaja2_3YAcqr_jHgtLVBidmM/edit?usp=sharing).
