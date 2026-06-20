# Day 1 Quiz: Encoding as Interpretation

These questions are ungraded self-assessments. Answer them before running the analysis
cells in the notebook — the goal is to make your assumptions explicit before the data does.

When you're done, close this tab and return to the notebook.

---

<div id="quiz-day1-quiz" class="jb-quiz-container"></div>
<script>
(function() {
  var questions = [{"question": "In kern notation, what does the exclamation mark (!!!) at the start of a line indicate?", "type": "multiple_choice", "answers": [{"answer": "A global metadata record (reference record)", "correct": true, "feedback": "Correct. Lines beginning with !!! are global reference records \u2014 metadata like title, composer, or collection information that applies to the whole file."}, {"answer": "A barline", "correct": false, "feedback": "Barlines in kern are indicated with = (e.g. =1, =2). The ! prefix marks metadata."}, {"answer": "A rest", "correct": false, "feedback": "Rests are encoded as 'r' in kern (e.g. 4r = quarter rest). The !!! prefix marks metadata."}, {"answer": "The end of a spine", "correct": false, "feedback": "Spine endings are marked with *- in kern. The !!! prefix marks global metadata records."}]}, {"question": "All tunes in the Beregovski corpus are notated in G, regardless of original performance pitch. Select ALL true consequences of this decision.", "type": "many_choice", "answers": [{"answer": "Pitch class 7 (G) always corresponds to scale degree 1", "correct": true, "feedback": "Correct. With G as tonic, G (pc 7) is always scale degree 1 \u2014 pitch class and scale degree are equivalent."}, {"answer": "Absolute pitch comparison and scale-degree comparison give equivalent results", "correct": true, "feedback": "Correct. Because all tunes share G as tonic, comparing absolute pitches and comparing scale degrees produce the same relative relationships."}, {"answer": "The augmented second characteristic of freygish will always appear between the same two pitch classes", "correct": true, "feedback": "Correct. In freygish notated in G, the augmented second always falls between Ab (pc 8) and B (pc 11), making it easy to identify computationally."}, {"answer": "The encoding faithfully represents the pitch at which tunes were originally performed", "correct": false, "feedback": "No \u2014 the G notation is a computational convenience, not a record of performance pitch. Beregovski's informants performed in various keys; the notation standardizes this away."}]}, {"question": "DARMS was designed so that non-musicians could encode scores affordably. What does this design goal build into the encoding system?", "type": "multiple_choice", "answers": [{"answer": "Spatial position on the staff is primary \u2014 notes are defined by where they sit on a grid, not by musical function", "correct": true, "feedback": "Correct. DARMS encodes notes by their spatial position (a number representing staff position), reflecting the goal of letting non-musicians encode visually without needing to interpret musical meaning."}, {"answer": "It encodes microtones and non-Western pitch systems by default", "correct": false, "feedback": "That was MUSTRAN's explicit goal, not DARMS. MUSTRAN was designed with extensibility for non-Western music in mind."}, {"answer": "It represents performance nuance like dynamics and articulation more richly than Humdrum", "correct": false, "feedback": "DARMS was designed for cheap and accessible encoding, not for expressive richness. Humdrum's kern format actually handles a wider range of musical information."}, {"answer": "Rhythm is implicit and derived from note position", "correct": false, "feedback": "DARMS does encode rhythm explicitly using letter codes (W=whole, H=half, Q=quarter, E=eighth, etc.)."}]}, {"question": "Humdrum kern represents polyphonic music by having multiple 'spines' (columns), with each moment in time as a new row. What analytical operation does this two-dimensional structure make especially easy?", "type": "multiple_choice", "answers": [{"answer": "Finding all simultaneous events at a specific moment", "correct": true, "feedback": "Correct. Because each row is a moment in time, a single row contains all simultaneous events across all voices \u2014 making vertical (harmonic) analysis straightforward."}, {"answer": "Representing indefinite pitch (like percussion)", "correct": false, "feedback": "Indefinite pitch is handled in kern with specific tokens, but it is not the primary advantage of the two-dimensional structure."}, {"answer": "Encoding continuous audio waveforms", "correct": false, "feedback": "Kern is a symbolic (score-based) format. It represents discrete note events, not continuous audio."}, {"answer": "Automatic transposition to any key", "correct": false, "feedback": "Transposition requires additional processing \u2014 the two-dimensional structure does not automatically handle this."}]}];
  var container = document.getElementById('quiz-day1-quiz');
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

*[← Back to Encoding as Interpretation notebook](../notebooks/day1_encoding.ipynb)*
