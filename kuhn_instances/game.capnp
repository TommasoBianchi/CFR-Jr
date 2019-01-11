@0xf8c775413760aa39;

struct Infoset {
  startSequenceId @0 :UInt32;
  endSequenceId @1 :UInt32;
  parentSequenceId @2 :UInt32;
}

struct Treeplex {
  infosets @0 :List(Infoset);
}

struct PayoffMatrix {
  entries @0 :List(Entry);

  struct Entry {
    sequencePl1 @0 :UInt32;
    sequencePl2 @1 :UInt32;
    sequencePl3 @2 :UInt32;

    payoffPl1 @3 :Float64;
    payoffPl2 @4 :Float64;
    payoffPl3 @5 :Float64;

    chanceFactor @6 :Float64;
  }
}

struct Game {
  treeplexPl1 @0 :Treeplex;
  treeplexPl2 @1 :Treeplex;
  treeplexPl3 @2 :Treeplex;

  payoffMatrix @3 :PayoffMatrix;
}
