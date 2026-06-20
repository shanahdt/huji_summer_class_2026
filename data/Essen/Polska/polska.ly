\version "2.7.40"
\header {
	crossRefNumber = "1"
	footnotes = ""
	tagline = "Lily was here 2.15.24 -- automatically converted from ABC"
	title = "Das Bauerntoechterlein Es hat ein Bauer ein Toechterlein,"
}
voicedefault =  {
\set Score.defaultBarType = "empty"

% %abc-version 2.0
 % %abcx-abcm2ps-target-version 5.9.1 (29 Sep 2008)
 % %abc-creator hum2abc beta
 % %abcx-conversion-date 2012/11/13 21:19:45
 % %abc-edited-by Helmut Schaffrath
 % %humdrum-veritas 540104439
 % %humdrum-veritas-data 847191817
 % %continueall 1
 % %barnumbers 0
 \time 6/8 \key bes \major       bes'8 -.(   a'8    g'8    a'4    f'!16    e'16 
   \bar "|"     d'4  -)       g'4 -.(   d'8    f'!8    e'8    f'!8    \bar "|"  
   d'4  -)       bes'8 -.(   a'8    c''8    a'8    g'8    fis'8    \bar "|"     
g'4  -)   \bar "|."   
}

\score{
    <<

	\context Staff="default"
	{
	    \voicedefault 
	}

    >>
	\layout {
	}
	\midi {}
}
