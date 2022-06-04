\header{
  title="Ode to Joy "
  composer=" Ludwig van Beethoven"
  tagline = \markup {
   \column {
   	  "This is footer"
	  " "
      "Created by MusicTXT and LilyPond"
    }
  }
}
melody_a=
 {\clef treble  \key c \major
  \time 4/4
  \tempo 4=140
   c'4 d'4 e'8f'8 g'4
   c'4 d'4 e'8f'8 g'4
   c'4 d'4 e'8f'8 g'4
   c'4 d'4 e'8f'8 g'4
}

melody = \partcombine \melody_None \melody_None
melody = \partcombine \melody \melody_a

chord=  { 
  \clef bass
  \key c \major

  \chordmode { c,1             d,1 e,1             f,1}}
\score {
  \new PianoStaff <<
  \chords { c,1             d,1 e,1             f,1}
  \new Staff = "up" \melody
  \addlyrics {   一}
  \new Staff = "down" \chord
  >>\layout { }
}

\score {
  \new PianoStaff \with {midiInstrument = #"acoustic grand"} <<
  \new Staff = "up" \melody
  \new Staff = "down" \chord
  >>\midi { }
}
\version "2.20.0-1"  % necessary for upgrading to future LilyPond versions.
