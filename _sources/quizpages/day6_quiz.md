# Day 6 Quiz: Audio Features and What They Measure

These questions are ungraded self-assessments. Answer them before running the analysis
cells in the notebook — the goal is to make your assumptions explicit before the data does.

When you're done, close this tab and return to the notebook.

---

<div id="quiz-day6-quiz" class="jb-quiz-container"></div>
<script>
(function() {
  var questions = [{"question": "A chromagram represents audio as a 12\u00d7T matrix (12 pitch classes \u00d7 time frames). How does this differ from the pitch class profile we computed from kern notation?", "type": "many_choice", "answers": [{"answer": "The chromagram includes a time dimension \u2014 pitch class energy varies frame by frame", "correct": true, "feedback": "Correct. A chromagram shows how pitch class content changes across time, not just the overall distribution. The score-based pitch class profile collapses time entirely."}, {"answer": "The chromagram is derived from acoustic energy, not from symbolic note events", "correct": true, "feedback": "Correct. Chroma features are computed from the frequency content of the audio signal using a constant-Q transform or similar. They do not know about 'notes' \u2014 just spectral energy at each pitch class."}, {"answer": "The chromagram cannot represent the augmented second characteristic of freygish", "correct": false, "feedback": "The chromagram will show energy at the pitch classes corresponding to the augmented second \u2014 it just represents them as energy distributions rather than symbolic intervals."}, {"answer": "The chromagram requires knowing the key before extraction", "correct": false, "feedback": "Chroma extraction is key-agnostic \u2014 it measures energy at all 12 pitch classes simultaneously. No prior key assumption is needed."}]}, {"question": "MFCCs (Mel-Frequency Cepstral Coefficients) are used to represent timbre in audio analysis. Spotify used MFCCs as part of what they called 'acousticness' and 'energy'. What do MFCCs primarily capture?", "type": "multiple_choice", "answers": [{"answer": "The spectral envelope of the sound \u2014 the overall shape of the frequency content, associated with instrument tone color", "correct": true, "feedback": "Correct. MFCCs compress the spectral envelope into a small number of coefficients. They are very sensitive to timbre (e.g. clarinet vs violin) but relatively insensitive to pitch and melody."}, {"answer": "The pitch of the fundamental frequency", "correct": false, "feedback": "Pitch tracking (F0 estimation) is a separate operation. MFCCs describe the spectral envelope, not the fundamental frequency."}, {"answer": "The tempo and rhythmic structure of the recording", "correct": false, "feedback": "Tempo and rhythm are estimated by separate algorithms (onset detection, beat tracking). MFCCs are a spectral feature."}, {"answer": "The loudness at each moment in time", "correct": false, "feedback": "Loudness is captured by RMS energy or similar measures. MFCCs describe spectral shape, which correlates loosely with timbre and roughness but is not primarily a loudness measure."}]}, {"question": "You compute the Pearson correlation between the corpus pitch class profile (from kern) and a chromagram mean (from a recording) and get r = 0.61. A colleague says this means 'the score and the recording agree about 61% of the time'. What is wrong with this interpretation?", "type": "multiple_choice", "answers": [{"answer": "Pearson r is not a percentage of agreement \u2014 it measures linear association between two profiles, not proportion of matching events", "correct": true, "feedback": "Correct. r=0.61 means the two 12-dimensional profiles are positively correlated \u2014 when one is high, the other tends to be high. It does not mean 61% of notes match or 61% of time frames agree."}, {"answer": "The correlation should be computed on the raw counts, not the proportions", "correct": false, "feedback": "Normalizing to proportions before correlating is standard and correct. The issue is the misinterpretation of r as a percentage, not the normalization choice."}, {"answer": "A correlation of 0.61 means the two sources are unrelated", "correct": false, "feedback": "r=0.61 is a moderate positive correlation \u2014 the sources are meaningfully related, not unrelated. The issue is the specific 'percentage of agreement' misreading."}, {"answer": "You cannot correlate score data with audio data", "correct": false, "feedback": "Correlating score-derived and audio-derived pitch profiles is a legitimate and informative operation. The issue is only the interpretation of what the correlation coefficient means."}]}];
  var container = document.getElementById('quiz-day6-quiz');
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

*[← Back to Audio Features and What They Measure notebook](../notebooks/day6_audio.ipynb)*
