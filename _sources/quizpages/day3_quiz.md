# Day 3 Quiz: N-grams and Melodic Tendency

These questions are ungraded self-assessments. Answer them before running the analysis
cells in the notebook — the goal is to make your assumptions explicit before the data does.

When you're done, close this tab and return to the notebook.

---

<div id="quiz-day3-quiz" class="jb-quiz-container"></div>
<script>
(function() {
  var questions = [{"question": "A melodic bigram is a pair of consecutive scale degrees (e.g. 1\u21922, 5\u21923). What does a high bigram frequency tell us, according to Huron's theory of musical expectation?", "type": "multiple_choice", "answers": [{"answer": "That transition is statistically common in the style, and listeners enculturated in that style have learned to expect it", "correct": true, "feedback": "Correct. Huron argues that statistical regularities in a corpus shape listener expectations through implicit learning. A high-frequency bigram is one that enculturated listeners have internalized as 'normal' or 'expected'."}, {"answer": "That transition is particularly expressive or emotionally significant", "correct": false, "feedback": "Frequency and expressiveness are different things. A common transition may be neutral background; rare transitions may carry expressive weight precisely because they violate expectation."}, {"answer": "That transition always occurs at metrically strong positions", "correct": false, "feedback": "Bigram frequency counts all occurrences regardless of metric position. Beat-strength filtering is a separate analytical step."}, {"answer": "That transition is unique to this repertoire and not found in other styles", "correct": false, "feedback": "Frequency within a corpus says nothing about uniqueness across corpora. You would need a comparative bigram analysis to identify style-specific transitions."}]}, {"question": "You extract the top-20 bigrams from freygish tunes and compute Jaccard similarity between the freygish bigram set and the minor bigram set. You get J = 0.38. What does this mean?", "type": "multiple_choice", "answers": [{"answer": "38% of the bigrams in the combined set appear in both modes' top-20 lists", "correct": true, "feedback": "Correct. Jaccard similarity = |intersection| / |union|. 0.38 means 38% of all unique bigrams across both lists are shared between the two modes."}, {"answer": "Freygish and minor are 38% similar overall", "correct": false, "feedback": "Jaccard similarity is specific to the feature set you chose \u2014 here, top-20 trigrams. It is not a global similarity measure between the modes as a whole."}, {"answer": "38% of freygish tunes are misclassified as minor", "correct": false, "feedback": "Jaccard similarity between bigram sets has nothing to do with classification accuracy. That is a different calculation entirely."}, {"answer": "The two modes share 38 bigrams", "correct": false, "feedback": "Jaccard is a proportion (0 to 1), not a count. J=0.38 means 38% of the union set is shared, but the actual count depends on how large the union is."}]}, {"question": "Beat-strength filtering means only analyzing note transitions that occur on metrically strong beats. What theoretical assumption motivates this choice?", "type": "multiple_choice", "answers": [{"answer": "Metrically strong notes are more perceptually salient and more likely to define the modal or tonal character of a melody", "correct": true, "feedback": "Correct. This assumption comes from theories of metrical hierarchy (Lerdahl & Jackendoff's GTTM) \u2014 notes on strong beats are structurally prominent and more likely to convey tonal function than passing tones on weak beats."}, {"answer": "Weak beats are more likely to contain errors in the kern encoding", "correct": false, "feedback": "Encoding accuracy is not related to metric position. This is a music-theoretic assumption about perceptual salience, not a data quality concern."}, {"answer": "It reduces the dataset size, making computation faster", "correct": false, "feedback": "Speed might be a side effect, but it is not the theoretical motivation. The reason is about what notes carry structural information."}, {"answer": "Strong beat notes are always chord tones in klezmer", "correct": false, "feedback": "Klezmer is monophonic in this corpus \u2014 there are no chords. And 'always' is too strong even for harmonic music. The claim is about salience, not about harmonic function."}]}, {"question": "The Beregovski corpus bigram data is available pre-computed on the companion website. Why might you still want to reproduce it yourself in Python?", "type": "many_choice", "answers": [{"answer": "To apply it to a specific subset (e.g. only bulgar tunes, or only one region)", "correct": true, "feedback": "Correct. The pre-computed data covers the full corpus. Reproducing it yourself lets you filter to any subset that matches your research question."}, {"answer": "To use different n values (trigrams, 4-grams) beyond what the website provides", "correct": true, "feedback": "Correct. The website provides bigram data. If you want trigrams or other n-gram sizes, you need to compute them yourself."}, {"answer": "Because the website data contains errors", "correct": false, "feedback": "There is no reason to assume errors. The website data is from the published paper. The motivation for recomputing is flexibility, not distrust."}, {"answer": "To apply the same pipeline to a different corpus (e.g. Charlie Parker) for comparison", "correct": true, "feedback": "Correct. Once you have the bigram extraction function working on Beregovski, you can run it on any other corpus in the same format to make direct comparisons."}]}];
  var container = document.getElementById('quiz-day3-quiz');
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

*[← Back to N-grams and Melodic Tendency notebook](../notebooks/day3_ngrams.ipynb)*
