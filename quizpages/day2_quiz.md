# Day 2 Quiz: Pitch Distributions and Mode

These questions are ungraded self-assessments. Answer them before running the analysis
cells in the notebook — the goal is to make your assumptions explicit before the data does.

When you're done, close this tab and return to the notebook.

---

<div id="quiz-day2-quiz" class="jb-quiz-container"></div>
<script>
(function() {
  var questions = [{"question": "A pitch class profile (sometimes called a key profile) represents a melody as 12 numbers. What do those 12 numbers count?", "type": "multiple_choice", "answers": [{"answer": "The proportion of notes belonging to each of the 12 pitch classes (C, C#, D... B), ignoring octave", "correct": true, "feedback": "Correct. A pitch class profile collapses all octaves \u2014 G3, G4, and G5 all count as pitch class 7 \u2014 and records what fraction of notes fall in each of the 12 chromatic pitch classes."}, {"answer": "The 12 most common melodic intervals in the piece", "correct": false, "feedback": "That would be an interval profile, not a pitch class profile. Pitch class profiles count pitch occurrences, not transitions between pitches."}, {"answer": "The 12 scale degrees present in the melody", "correct": false, "feedback": "Scale degrees are relative to a tonic (1=tonic, 2=supertonic...). Pitch classes are absolute (C=0, C#=1...). The profiles look similar but encode different things."}, {"answer": "The number of times each of 12 rhythmic values appears", "correct": false, "feedback": "That would be a rhythm histogram. Pitch class profiles only concern pitch, not rhythm."}]}, {"question": "The Krumhansl-Schmuckler key-finding algorithm correlates a melody's pitch class profile against pre-computed major and minor key templates. Those templates came from probe-tone experiments with Western listeners. Select ALL the reasons this algorithm is likely to struggle with freygish (ahavah rabbah).", "type": "many_choice", "answers": [{"answer": "Freygish uses an augmented second, a pitch interval absent from Western major and minor scales", "correct": true, "feedback": "Correct. The augmented second between scale degrees 2 and 3 in freygish (e.g. Ab and B in G freygish) has no equivalent in major or minor, so the algorithm has no template that fits this characteristic feature."}, {"answer": "The KS templates were derived from listeners trained in Western tonal music, who had no exposure to klezmer modes", "correct": true, "feedback": "Correct. Probe-tone ratings reflect the internalized expectations of the listener population. Western-trained listeners rate probe tones differently from how klezmer musicians would."}, {"answer": "Freygish has the same pitch content as Western Phrygian dominant, which has its own KS template", "correct": false, "feedback": "The KS algorithm only has templates for the 24 major and minor keys \u2014 there is no Phrygian dominant template. Freygish would be forced into the nearest major or minor match."}, {"answer": "The algorithm cannot process kern files directly", "correct": false, "feedback": "music21 can parse kern and then apply key-finding algorithms to the resulting Score object. The file format is not the issue."}]}, {"question": "You compute the Pearson correlation between a tune's pitch class profile and the KS major template and get r = 0.42. You then compute the correlation with the KS minor template and get r = 0.71. What does the algorithm report?", "type": "multiple_choice", "answers": [{"answer": "The tune is in a minor key, because that template has the higher correlation", "correct": true, "feedback": "Correct. The KS algorithm reports the key whose template has the highest correlation with the tune's pitch profile. r=0.71 (minor) > r=0.42 (major), so it reports minor."}, {"answer": "The tune is in a major key, because major is more common in Western music", "correct": false, "feedback": "The algorithm makes no assumption about frequency of major vs minor. It simply reports the highest correlation."}, {"answer": "The result is ambiguous because neither correlation is above 0.8", "correct": false, "feedback": "The KS algorithm always reports the single best-matching key regardless of absolute correlation strength. The correlationCoefficient attribute in music21 reports the winning score, not a threshold."}, {"answer": "The tune is in a mode unrelated to major or minor", "correct": false, "feedback": "The KS algorithm can only report one of the 24 major/minor keys \u2014 it has no category for 'other mode'. It will force-fit freygish into whichever major or minor key it most resembles."}]}, {"question": "In the Beregovski corpus, what is the most theoretically interesting reason to compare mode profiles across genres (e.g. freylekhs vs dobranoch)?", "type": "multiple_choice", "answers": [{"answer": "To test whether modal choice is genre-specific or cuts across genres, which would reveal whether mode and dance function are coupled in this repertoire", "correct": true, "feedback": "Correct. If certain modes cluster with certain genres, it suggests mode is tied to social function (dance type, occasion). If modes are evenly distributed across genres, mode may be a more independent musical parameter."}, {"answer": "To check whether Malin made errors in his mode annotations", "correct": false, "feedback": "Cross-tabulating mode and genre would not reveal annotation errors \u2014 Malin's annotations and Beregovski's genre labels are independent. Errors would require comparing against a separate source of ground truth."}, {"answer": "Because the key-finding algorithm performs better on some genres than others", "correct": false, "feedback": "This might be true but it is not the primary theoretical interest. The deeper question is about the relationship between modal identity and musical/social function."}, {"answer": "To normalize the pitch profiles before clustering", "correct": false, "feedback": "Genre-mode cross-tabulation is an analytical question, not a preprocessing step for normalization."}]}];
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
