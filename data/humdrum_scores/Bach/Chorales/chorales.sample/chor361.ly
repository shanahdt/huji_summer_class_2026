\version "2.7.40"
\header {
	composer = "Johann Sebastian Bach"
	crossRefNumber = "1"
	footnotes = ""
	tagline = "Lily was here 2.18.2 -- automatically converted from ABC"
	title = "Du Lebensfuerst, Herr Jesu Christ"
}
voiceB =  {
\set Score.defaultBarType = ""

g'4  \bar "|"   g'4    a'4    b'8    cis''8    d''4    \bar "|"   d''4    
cis''4    c''!4    b'4    a'4    b'4    \bar "|"   a'2    g'4    a'4    b'8    
cis''8    d''4    \bar "|"   d''4    cis''4    c''!4    b'4    a'4    b'4    
\bar "|"   a'2    a'4    b'4    c''4    c''4    \bar "|"   b'8    a'8    b'4    
b'4    b'4    c''8    d''8    e''4    \bar "|"   e''4    dis''4    g''4    b'4  
  c''4    b'4    \bar "|"   a'2    e''4    d'4    c''4    b'8    c''8    
\bar "|"   a'2    
}
voiceC =  {
\set Score.defaultBarType = ""

d'4    \bar "|"   e'4    fis'4    d'8    e'8    fis'4    \bar "|"   e'8    
fis'8    g'4    e'4    d'8    e'8    fis'!4    g'4    \bar "|"   g'4    fis'4   
 e'4    fis'!4    d'8    e'8    fis'4    \bar "|"   e'8    fis'8    g'4    e'4  
  d'8    e'8    fis'!4    g'4    \bar "|"   g'4    fis'4    a'4   ~    a'8    
gis'8    a'8    gis'8    a'4    \bar "|"   a'4    gis'4    e'4    e'4    e'8    
fis'8    gis'8    fis'8    \bar "|"   fis'8    g'8    a'4    g'8    a'8    b'4  
  b'8    a'8    a'8    g'8    \bar "|"   g'2    e'4    fis'4    g'8    a'8    
d'4    \bar "|"   e'4    d'4    
}
voiceD =  {
\set Score.defaultBarType = ""

b4    \bar "|"   b8    c'8   ~    c'8    d'8    b8    a8    a4    \bar "|"   a4 
   a4    g8    a8    b8    c'8    d'4    d'4    \bar "|"   d'4.    c'8    b8    
c'8   ~    c'8    d'8    b8    a8    a4    \bar "|"   a4    a4    g8    a8    
b8    c'8    d'4    d'4    \bar "|"   d'4.    c'8    fis'8    e'8    d'4    e'4 
   fis'4    \bar "|"   b4    e'8    d'8    b8    c'8    d'8    e'8    c'4    
cis'4    \bar "|"   b4    b4    d'4    g'4    g8    a8    b4    \bar "|"   e'8  
  d'8    e'8    cis'8    d'8    cis'8    cis'8    b8    b8    a8    g4    
\bar "|"   g8    fis16    e16    fis4    
}
voiceE =  {
\set Score.defaultBarType = ""

\key c \major g8    fis8    \bar "|"   e4    d4    g4    fis8    g8    \bar "|" 
  a4    a,4    e8    fis8    g8    c8    c'8    b8    a8    g8    \bar "|"   
d'4    d4    e4    d4    g4    fis8    g8    \bar "|"   a4    a,4    e8    fis8 
   g8    c8    c'8    b8    a8    g8    \bar "|"   d'4    d4    d'8    cis'8    
b4    a4    dis4    \bar "|"   e4    e4    g4    gis4    a4    ais4    \bar "|" 
  b4    b,4    b8    a8    g8    fis8    e8    fis8    g8    e8    \bar "|"   
cis8    b,8    cis8    a,8    cis4    d4    e8    fis8    g4    \bar "|"   c4   
 d4    
}
voicedefault =  {
\set Score.defaultBarType = ""

% %abc-version 2.0
 % %abcx-abcm2ps-target-version 5.9.1 (29 Sep 2008)
 % %abc-creator hum2abc beta
 % %abcx-conversion-date 2019/02/10 22:18:17
 % %abc-copyright Copyright 1992 David Huron
 % %abc-edited-by David Huron
 % %abc-edited-by David Huron
 % %humdrum-veritas 1517959309
 % %humdrum-veritas-data 644463231
 % %continueall 1
 % %barnumbers 0
 \time 4/4 % %staves [1 2 3 4]
 
}

\score{
    <<

	\context Staff="1"
	{
	    \voicedefault
	    \voiceB 
	}

	\context Staff="2"
	{
	    \voicedefault
	    \voiceC 
	}

	\context Staff="3"
	{
	    \voicedefault
	    \voiceD 
	}

	\context Staff="4"
	{
	    \voicedefault
	    \voiceE 
	}

    >>
	\layout {
	}
	\midi {}
}
