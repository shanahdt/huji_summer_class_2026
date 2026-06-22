# Day 2 Quiz: N-Grams, etc.

These questions are ungraded self-assessments. Answer them before running the analysis
cells in the notebook — the goal is to make your assumptions explicit before the data does.

When you're done, close this tab and return to the notebook.

---

<div id="quiz-day2-quiz" class="jb-quiz-container"></div>
<script>
(function() {
  var questions = [
  {
  "question": "The notebook compares Charlie Parker and Dizzy Gillespie using scale-degree bigrams estimated relative to each piece's detected key. What is the main analytical risk of this approach for jazz?",
  "type": "multiple_choice",
  "answers": [
    {
      "answer": "The Omnibook transcriptions are not in kern format so the parser cannot read them",
      "correct": false,
      "feedback": "The data files are in kern format — that's not the issue. The risk is in the analytical interpretation of the scale degrees, not in the file parsing."
    },
        {
      "answer": "Jazz uses heavy chromaticism and chord substitutions, so many notes don't belong to the detected key — mapping them to a major scale loses their function",
      "correct": true,
      "feedback": "Correct. A bebop line over a ii–V–I might include tritone substitutions, passing tones, and altered tensions that the key-detection algorithm maps incorrectly. The scale-degree representation is a simplifying choice that works better for diatonic repertoire."
    },
    {
      "answer": "Parker and Gillespie play in different keys so scale degrees cannot be compared",
      "correct": false,
      "feedback": "The code normalizes to scale degrees relative to the detected tonic for each piece, so absolute key is not the problem. The issue is that the tonal language of bebop is not well-described by a single major scale."
    },
    {
      "answer": "Bigrams can only capture diatonic music and throw an error on chromatic passages",
      "correct": false,
      "feedback": "The code handles chromatic notes by mapping them to the nearest scale degree or filtering them out with `if degree is not None`. No error is thrown — but the mapping silently loses information about chromatic function."
    }
  ]
    },
    {
  "question": "The notebook represents bigrams as a transition matrix — a grid where rows are 'from' notes and columns are 'to' notes, and each cell contains a count or percentage. What does a row in the percentage version tell you?",
  "type": "multiple_choice",
  "answers": [
    {
      "answer": "How many times note X appeared in the corpus overall",
      "correct": false,
      "feedback": "That would be a unigram count (pitch histogram), not a bigram transition matrix. The matrix specifically captures what follows each note, not how often the note itself occurs."
    },
    {
      "answer": "The most common note in the corpus for each starting pitch",
      "correct": false,
      "feedback": "The row shows the full distribution of following notes, not just the single most common one. Reading only the highest cell would lose information about the full transition profile."
    },
    {
      "answer": "The percentage of the melody that consists of that note",
      "correct": false,
      "feedback": "That would be the pitch class profile from Day 1. The transition matrix is about movement between notes, not about how often any single note appears."
    },
        {
      "answer": "Given that a melody is currently on note X, the probability of each possible next note",
      "correct": true,
      "feedback": "Correct. Each row sums to 100%. If you're on G4, the row for G4 tells you how often each other note followed G4 in this corpus — a conditional probability distribution."
    }
  ]
},
{
  "question": "The notebook shows Huron's scale-degree transition tables. According to Huron, why do listeners expect certain melodic transitions more than others?",
  "type": "multiple_choice",
  "answers": [
    {
      "answer": "Because those transitions are inherently more consonant or pleasant",
      "correct": false,
      "feedback": "Consonance is a separate property. A transition like 7→1 is expected because of statistical frequency in tonal music, not because it is inherently more consonant than other intervals."
    },
    {
      "answer": "Because composers intentionally write the most common transitions to please listeners",
      "correct": false,
      "feedback": "Huron's account is statistical and cultural, not intentional. Composers absorb stylistic norms and reproduce them — but the norms emerge from the corpus as a whole, not from individual decisions."
    },
        {
      "answer": "Because those transitions are statistically frequent in the music they grew up hearing, and listeners internalize these patterns through exposure",
      "correct": true,
      "feedback": "Correct. Huron's expectation theory holds that statistical regularities in a musical culture shape listener predictions through implicit learning — the same mechanism that makes Q→U feel 'obvious' in English spelling."
    },
    {
      "answer": "Because music theory rules prescribe which melodic intervals are permitted",
      "correct": false,
      "feedback": "Music theory describes norms after the fact. Huron is making a psychological and statistical claim about expectation, which can exist even for patterns that no theory explicitly prescribes."
    }
  ]
}
  ];
  var container = document.getElementById('quiz-day2-quiz');
  var answered = {};
  if (!document.getElementById('jb-quiz-style')) {
    var style = document.createElement('style');
    style.id = 'jb-quiz-style';
    style.textContent = '.jb-quiz-container{font-family:-apple-system,sans-serif;margin:1em 0 2em}.jb-question{background:#f8f9fa;border-left:4px solid #4c72b0;border-radius:4px;padding:1em 1.2em;margin-bottom:1.2em}.jb-qtext{font-weight:600;margin-bottom:.6em;font-size:.95em}.jb-qnum{display:inline-block;background:#4c72b0;color:#fff;font-size:.75em;padding:1px 8px;border-radius:10px;margin-right:6px}.jb-qtype{font-size:.8em;color:#666;font-style:italic;margin-bottom:.7em}.jb-answers{display:flex;flex-direction:column;gap:6px}.jb-btn{display:flex;align-items:flex-start;gap:8px;padding:8px 12px;border:1.5px solid #dee2e6;border-radius:5px;background:#fff;cursor:pointer;text-align:left;font-size:.88em;font-family:inherit;color:#212529;width:100%;transition:all .15s}.jb-btn:hover:not(:disabled){border-color:#4c72b0;background:#e8eef8}.jb-btn:disabled{cursor:default}.jb-btn.correct{border-color:#198754;background:#d1e7dd}.jb-btn.incorrect{border-color:#dc3545;background:#f8d7da}.jb-btn.missed{border-color:#198754;background:#d1e7dd;opacity:.7}.jb-btn.dim{opacity:.45}.jb-icon{font-size:1em;flex-shrink:0;width:16px}.jb-feedback{font-size:.8em;color:#555;font-style:italic;display:block;margin-top:4px}.jb-check{margin-top:8px;padding:6px 14px;background:#4c72b0;color:#fff;border:none;border-radius:4px;cursor:pointer;font-size:.88em;font-family:inherit}.jb-check:hover{background:#3a5a9a}.jb-numeric-row{display:flex;gap:8px;align-items:center;margin-bottom:6px}.jb-input{font-family:monospace;padding:6px 8px;border:1.5px solid #dee2e6;border-radius:4px;width:120px;font-size:.88em}.jb-fb-box{padding:7px 12px;border-radius:4px;font-size:.85em;display:none;margin-top:4px}.jb-fb-box.correct{background:#d1e7dd;color:#0a3622;display:block}.jb-fb-box.incorrect{background:#f8d7da;color:#58151c;display:block}.jb-hint{font-size:.8em;color:#666;font-style:italic;margin-bottom:6px}.jb-score{background:#fff3cd;border:1px solid #ffc107;border-radius:4px;padding:8px 14px;font-size:.88em;margin-top:.5em;display:none}.jb-score.show{display:block}';
    document.head.appendChild(style);
  }
  var scoreEl = document.createElement('div');
  scoreEl.className = 'jb-score';
  function checkAllDone() {
    if (Object.keys(answered).length === questions.length) {
      var c = Object.values(answered).filter(Boolean).length;
      scoreEl.textContent = 'Score: ' + c + ' / ' + questions.length;
      scoreEl.className = 'jb-score show';
    }
  }
  questions.forEach(function(q, qi) {
    var qDiv = document.createElement('div'); qDiv.className = 'jb-question';
    var qText = document.createElement('div'); qText.className = 'jb-qtext';
    qText.innerHTML = '<span class="jb-qnum">Q'+(qi+1)+'</span>'+q.question;
    qDiv.appendChild(qText);
    var qType = document.createElement('div'); qType.className = 'jb-qtype';
    qType.textContent = q.type==='multiple_choice'?'Select one correct answer':q.type==='many_choice'?'Select ALL that apply':'Enter a numeric answer';
    qDiv.appendChild(qType);
    if (q.type === 'multiple_choice') {
      var aDiv = document.createElement('div'); aDiv.className = 'jb-answers';
      q.answers.forEach(function(ans, ai) {
        var btn = document.createElement('button'); btn.className = 'jb-btn';
        btn.innerHTML = '<span class="jb-icon">&#9675;</span><span class="jb-atext">'+ans.answer+'</span>';
        btn.addEventListener('click', function() {
          if (answered[qi]!==undefined) return;
          answered[qi] = ans.correct;
          aDiv.querySelectorAll('.jb-btn').forEach(function(b,bi) {
            b.disabled=true;
            var icon=b.querySelector('.jb-icon'), txt=b.querySelector('.jb-atext');
            if (bi===ai) {
              b.classList.add(ans.correct?'correct':'incorrect');
              icon.textContent=ans.correct?'✓':'✗';
              var fb=document.createElement('span'); fb.className='jb-feedback';
              fb.textContent=ans.feedback; txt.appendChild(fb);
            } else if (q.answers[bi].correct) {
              b.classList.add('correct'); icon.textContent='✓';
            } else { b.classList.add('dim'); icon.textContent='○'; }
          }); checkAllDone();
        });
        aDiv.appendChild(btn);
      }); qDiv.appendChild(aDiv);
    } else if (q.type === 'many_choice') {
      var aDiv=document.createElement('div'); aDiv.className='jb-answers';
      var sel={}, btnEls=[];
      q.answers.forEach(function(ans,ai) {
        var btn=document.createElement('button'); btn.className='jb-btn';
        btn.innerHTML='<span class="jb-icon">&#9633;</span><span class="jb-atext">'+ans.answer+'</span>';
        btn.addEventListener('click',function() {
          if (answered[qi]!==undefined) return;
          sel[ai]=!sel[ai];
          btn.querySelector('.jb-icon').textContent=sel[ai]?'☑':'□';
        });
        aDiv.appendChild(btn); btnEls.push(btn);
      });
      var chk=document.createElement('button'); chk.className='jb-check';
      chk.textContent='Check answers';
      chk.addEventListener('click',function() {
        if (answered[qi]!==undefined) return;
        var ok=true;
        q.answers.forEach(function(ans,ai) {
          var b=btnEls[ai]; b.disabled=true;
          var icon=b.querySelector('.jb-icon'), txt=b.querySelector('.jb-atext'), was=!!sel[ai];
          if (ans.correct&&was){b.classList.add('correct');icon.textContent='✓';}
          else if (ans.correct&&!was){b.classList.add('missed');icon.textContent='✓ (missed)';ok=false;}
          else if (!ans.correct&&was){b.classList.add('incorrect');icon.textContent='✗';ok=false;}
          else{b.classList.add('dim');icon.textContent='□';}
          if (was||ans.correct){
            var fb=document.createElement('span');fb.className='jb-feedback';
            fb.textContent=ans.feedback;txt.appendChild(fb);
          }
        });
        answered[qi]=ok; chk.disabled=true; checkAllDone();
      });
      qDiv.appendChild(aDiv); qDiv.appendChild(chk);
    } else if (q.type === 'numeric') {
      var correctVal=null, feedbackText='';
      if (q.answers&&q.answers[0]){
        correctVal=q.answers[0].value!==undefined?q.answers[0].value:q.answers[0].correct;
        feedbackText=q.answers[0].feedback||'';
      }
      if (q.hint){
        var h=document.createElement('div');h.className='jb-hint';
        h.textContent='Hint: '+q.hint;qDiv.appendChild(h);
      }
      var row=document.createElement('div');row.className='jb-numeric-row';
      var inp=document.createElement('input');inp.type='number';inp.step='0.01';
      inp.className='jb-input';inp.placeholder='Answer';
      var chk2=document.createElement('button');chk2.className='jb-check';chk2.textContent='Check';
      var fb=document.createElement('div');fb.className='jb-fb-box';
      chk2.addEventListener('click',function(){
        if(answered[qi]!==undefined)return;
        var val=parseFloat(inp.value);
        if(isNaN(val)){fb.className='jb-fb-box incorrect';fb.textContent='Please enter a number.';return;}
        var ok=Math.abs(val-correctVal)<=0.01;
        answered[qi]=ok;inp.disabled=true;chk2.disabled=true;
        fb.className='jb-fb-box '+(ok?'correct':'incorrect');
        fb.textContent=(ok?'✓ ':'✗ Not quite. ')+feedbackText;
        checkAllDone();
      });
      row.appendChild(inp);row.appendChild(chk2);
      qDiv.appendChild(row);qDiv.appendChild(fb);
    }
    container.appendChild(qDiv);
  });
  container.appendChild(scoreEl);
})();
</script>

---

*[← Back to Pitch Distributions and Mode notebook](../notebooks/day2_pitch_mode.ipynb)*
