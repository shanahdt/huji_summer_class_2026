# Day 7 Quiz: Mode Detection and Clustering

These questions are ungraded self-assessments. Answer them before running the analysis
cells in the notebook — the goal is to make your assumptions explicit before the data does.

When you're done, close this tab and return to the notebook.

---

<div id="quiz-day7-quiz" class="jb-quiz-container"></div>
<script>
(function() {
  var questions = [{"question": "PCA (Principal Component Analysis) reduces a high-dimensional feature matrix to 2 dimensions for visualization. What is the key thing you must remember when interpreting a PCA plot?", "type": "multiple_choice", "answers": [{"answer": "The axes (PC1, PC2) are linear combinations of the original features \u2014 their musical meaning must be inferred, not assumed", "correct": true, "feedback": "Correct. PC1 might correlate with 'mode' or 'range' or some combination of features, but PCA does not label its axes. Interpreting what PC1 represents requires examining the feature loadings and relating them back to musical properties."}, {"answer": "Points close together in PCA space are definitely musically similar", "correct": false, "feedback": "PCA proximity reflects similarity in the feature space you chose, not musical similarity in any absolute sense. Two tunes might appear close because they share pitch class distributions while differing substantially in melodic shape or rhythm."}, {"answer": "The percentage of explained variance (e.g. 'PC1 explains 34%') tells you how musically important that dimension is", "correct": false, "feedback": "Explained variance tells you how much of the statistical variance in the feature matrix is captured by that component \u2014 not how musically meaningful the dimension is."}, {"answer": "PCA requires that features be measured in the same units", "correct": false, "feedback": "PCA does require that features be scaled (standardized to zero mean and unit variance) before application, but not that they be in the same original units. StandardScaler handles this."}]}, {"question": "Your mode detector confuses freygish with minor more often than any other pair. Select ALL the musically plausible explanations for this confusion.", "type": "many_choice", "answers": [{"answer": "Freygish and minor share several pitch classes \u2014 both use G, D, C, and A prominently", "correct": true, "feedback": "Correct. The pitch profiles of freygish and minor overlap substantially, especially for the most common scale degrees. The augmented second pitches (Ab, B) are the main distinguishing features."}, {"answer": "Some tunes in the corpus modulate between freygish and minor within the same piece", "correct": true, "feedback": "Correct. Malin's annotations document within-tune modulations. A tune that moves between freygish and minor will have a blended pitch profile that the detector struggles to classify."}, {"answer": "The detector was trained on the same tunes it is evaluating", "correct": true, "feedback": "Correct. Building mode profiles from the full corpus and then evaluating on the same corpus means the profiles are not independent of the test data. This inflates apparent accuracy and can obscure systematic confusions."}, {"answer": "The kern encoding loses the augmented second because it cannot represent microtones", "correct": false, "feedback": "The augmented second is not a microtone \u2014 it is a diatonic interval fully representable in standard kern notation. Ab and B are both standard pitches."}]}, {"question": "You run k-means clustering with k=4 (matching the number of modes) on the Beregovski feature matrix. The resulting clusters do NOT align with Malin's mode labels. What are the two most constructive interpretations of this result?", "type": "many_choice", "answers": [{"answer": "The features you chose do not capture the information that distinguishes the modes \u2014 different features might cluster better", "correct": true, "feedback": "Correct. If pitch class profiles alone do not produce mode-aligned clusters, adding interval features, phrase-ending scale degrees, or bigram distributions might do better."}, {"answer": "The clustering has discovered a different, potentially musically meaningful structure in the corpus \u2014 worth investigating rather than dismissing", "correct": true, "feedback": "Correct. Clusters might align with genre, region, or instrument rather than mode. A mismatch with mode labels is not a failure \u2014 it may reveal that the corpus has more interesting structure than the four-mode taxonomy suggests."}, {"answer": "Malin's annotations must be wrong", "correct": false, "feedback": "Malin's annotations reflect expert musical judgment informed by deep knowledge of the repertoire. A clustering algorithm using pitch class profiles has no grounds to override that judgment \u2014 rather, the mismatch is information about what the algorithm is (and isn't) measuring."}, {"answer": "k=4 was the wrong number of clusters and you should try k=8", "correct": false, "feedback": "Changing k without a principled reason is a form of p-hacking. The choice of k=4 was theoretically motivated. If you try other values, you need to justify them and use cluster quality metrics (silhouette score, etc.) rather than just matching expectations."}]}];
  var container = document.getElementById('quiz-day7-quiz');
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

*[← Back to Mode Detection and Clustering notebook](../notebooks/day7_clustering.ipynb)*
