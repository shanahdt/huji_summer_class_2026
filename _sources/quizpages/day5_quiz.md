# Day 5 Quiz: Metadata and the Collector's Categories

These questions are ungraded self-assessments. Answer them before running the analysis
cells in the notebook — the goal is to make your assumptions explicit before the data does.

When you're done, close this tab and return to the notebook.

---

<div id="quiz-day5-quiz" class="jb-quiz-container"></div>
<script>
(function() {
  var questions = [{"question": "You run a chi-square test of independence on mode \u00d7 genre and get \u03c7\u00b2=24.3, p=0.002. What can you conclude?", "type": "multiple_choice", "answers": [{"answer": "There is a statistically significant association between mode and genre in this corpus", "correct": true, "feedback": "Correct. p=0.002 is well below the conventional threshold of 0.05, so we reject the null hypothesis of independence. Mode and genre are not distributed independently of each other in this corpus."}, {"answer": "Mode causes genre \u2014 freygish tunes became freylekhs because of their mode", "correct": false, "feedback": "Chi-square tests association, not causation. A significant result tells us the two variables co-vary; it says nothing about which (if either) causes the other."}, {"answer": "The result is musically meaningful", "correct": false, "feedback": "Statistical significance and musical meaningfulness are different things. A significant association might reflect the music, the communities Beregovski documented, his collection methodology, or some combination. Statistical significance alone does not settle this."}, {"answer": "You would get the same result in any klezmer corpus", "correct": false, "feedback": "This result is specific to this corpus collected by this collector in this region and period. Generalizing beyond Beregovski's collection requires additional evidence."}]}, {"question": "Beregovski collected tunes from musicians who had learned them in specific communities. Some metadata records that a musician learned a tune in a different location from where it was collected. Select ALL the questions this 'traveled tune' information could help answer.", "type": "many_choice", "answers": [{"answer": "Whether tunes change melodically as they travel between communities", "correct": true, "feedback": "Correct. If you have multiple versions of tunes with different origin/collection location pairs, you could test whether traveled tunes show greater melodic variation from local versions."}, {"answer": "Whether certain modes were more portable (traveled more) than others", "correct": true, "feedback": "Correct. If freygish tunes appear disproportionately among traveled tunes, that would suggest something about freygish's cultural mobility or prestige."}, {"answer": "The exact route a tune took between communities", "correct": false, "feedback": "The metadata only records origin and collection location \u2014 not intermediate stops. Reconstructing transmission routes would require additional historical or musicological evidence."}, {"answer": "Whether geographic distance between origin and collection correlates with melodic difference", "correct": true, "feedback": "Correct. If you geocode the locations and compute distances, you could test whether tunes that traveled farther changed more \u2014 a hypothesis about oral transmission and distance."}]}, {"question": "When you find a significant association between mode and region in Beregovski's corpus, you need to ask whether it reflects the music, the communities, or the collection. Which of the following would most help you distinguish between these interpretations?", "type": "multiple_choice", "answers": [{"answer": "Comparing the result to a second, independently collected corpus of klezmer from overlapping regions", "correct": true, "feedback": "Correct. If the mode-region association appears in both corpora, it is more likely to reflect genuine musical or community patterns. If it only appears in Beregovski, it may reflect his collection choices."}, {"answer": "Running the chi-square test again with a different significance threshold", "correct": false, "feedback": "Changing the threshold does not change the result or help distinguish between interpretations. It only changes how we label the same p-value."}, {"answer": "Using a larger n-gram window in the bigram analysis", "correct": false, "feedback": "Bigram window size is a different analytical parameter entirely. It would not help distinguish musical from collector-based explanations of mode-region association."}, {"answer": "Reading Slobin (1986) on Beregovski's collection methodology", "correct": true, "feedback": "Also correct. Slobin's analysis of Beregovski's research practices is essential context for interpreting any pattern in the corpus. Understanding who Beregovski talked to, where, and why can illuminate whether regional patterns reflect the music or the collector."}]}];
  var container = document.getElementById('quiz-day5-quiz');
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

*[← Back to Metadata and the Collector's Categories notebook](../notebooks/day5_metadata.ipynb)*
