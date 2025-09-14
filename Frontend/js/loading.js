(function () {
  const streamContainer = document.getElementById('streamContainer');
  const videoEl = document.getElementById('loadingVideo');
  const videoPlaceholder = document.getElementById('videoPlaceholder');

  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const wait = (ms) => new Promise(res => setTimeout(res, ms));

  async function typeChars(el, html, perCharMs = 4) {
    if (prefersReduced) {
      el.innerHTML = html;
      streamContainer.appendChild(el);
      return;
    }
    
    // Create a temporary element to extract text content
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    const text = tmp.textContent || tmp.innerText || ''; // stream as text to avoid half-open tags
    
    el.textContent = '';
    streamContainer.appendChild(el);
    
    for (let i = 0; i < text.length; i++) {
      el.textContent += text[i];
      // micro-yield for UI
      await wait(perCharMs);
    }
    
    // After typing is complete, set the full HTML content if it contains markup
    if (html !== text) {
      el.innerHTML = html;
    }
  }

  function appendBlock(node) {
    streamContainer.appendChild(node);
  }

  function line(tag, className, html) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    el.innerHTML = html;
    return el;
  }

  function analysisBox(lines) {
    const box = document.createElement('div');
    box.className = 'analysis-box';
    const head = document.createElement('p');
    head.innerHTML = '🤖 <strong>Analysis</strong>';
    const ul = document.createElement('ul');
    ul.className = 'analysis-list';
    lines.forEach(l => {
      const li = document.createElement('li');
      li.textContent = l;
      ul.appendChild(li);
    });
    box.appendChild(head);
    box.appendChild(ul);
    return box;
  }

  async function renderStreamForAddress(entry) {
    // Heading
    await typeChars(line('h2', 'section-heading', entry.heading), entry.heading, 5);
    await wait(5);
    
    // Subheading
    await typeChars(line('h3', 'section-subheading', entry.subheading), entry.subheading, 5);
    await wait(5);
    
    // Summary bold
    await typeChars(line('p', 'summary-bold', `<strong>${entry.summary_bold}</strong>`), entry.summary_bold, 5);
    await wait(5);

    // Separator
    appendBlock(line('pre', 'separator', '------------------------------------------------------------'));
    await wait(5);

    // Process each result
    for (const r of entry.results) {
      // Result title
      await typeChars(
        line('p', 'result-title', `<strong>${r.n}.</strong> ${r.title}`), 
        `${r.n}. ${r.title}`, 
        5
      );
      await wait(5);
      
      // Result link
      await typeChars(
        line('p', 'result-link', `🔗 <a href="${r.url_label}" target="_blank" rel="noopener">${r.url_label}</a>`),
        `🔗 ${r.url_label}`,
        5
      );
      await wait(5);
      
      // Analyzing line
      await typeChars(line('p', 'result-analyzing', r.analyzing), r.analyzing, 5);
      await wait(5);

      // Analysis box
      const box = analysisBox(r.analysis || []);
      appendBlock(box);
      await wait(5);

      // Separator
      appendBlock(line('pre', 'separator', '------------------------------------------------------------'));
      await wait(5);
    }

    // Footer italics are now handled by the separate Footer_Italics box
    // No need to render them here anymore
  }

  async function renderFallbackContent(heading, subheading) {
    await typeChars(line('h2', 'section-heading', heading), heading, 5);
    await wait(5);
    await typeChars(line('h3', 'section-subheading', subheading), subheading, 5);
    await wait(5);
    
    // Add a fallback link
    const fallbackLink = line('p', '', '<a href="results.html" style="color: #667eea; text-decoration: underline;">Continue to results →</a>');
    appendBlock(fallbackLink);
  }

  // Create and manage the Footer_Italics box
  function createFooterItalicsBox() {
    const box = document.createElement('div');
    box.id = 'footerItalicsBox';
    box.style.cssText = `
      background: transparent;
      border: 2px solid #4b5563;
      border-radius: 0.5rem;
      padding: 1rem;
      margin: 1rem auto;
      max-width: 600px;
      text-align: center;
      font-size: 1rem;
      font-weight: 600;
      color: #374151;
      transition: border-color 0.3s ease;
    `;
    box.textContent = '🔎Analyzing Data Records..';
    
    // Insert the box after the video section and before the divider
    const videoWrap = document.getElementById('videoWrap');
    const divider = document.querySelector('.divider');
    videoWrap.parentNode.insertBefore(box, divider);
    
    return box;
  }

  async function updateFooterItalicsBox(box, footerItalicsContent) {
    // Change border to red
    box.style.borderColor = '#dc2626';
    
    // Clear current content
    box.textContent = '';
    
    // Stream the footer_italics content
    if (prefersReduced) {
      box.innerHTML = `<em>${footerItalicsContent}</em>`;
      return;
    }
    
    // Type out the content character by character
    for (let i = 0; i < footerItalicsContent.length; i++) {
      box.textContent += footerItalicsContent[i];
      await wait(5); // Same speed as other footer-italics content
    }
    
    // After typing is complete, set italic formatting
    box.innerHTML = `<em>${footerItalicsContent}</em>`;
  }

  async function main() {
    try {
      // Handle video - use the specific video file from Frontend directory
      const videoPath = 'BrowserUseCountySearchCropped.mp4';
      videoEl.src = videoPath;
      videoEl.style.display = 'block';
      videoPlaceholder.style.display = 'none';
      
      // Handle video load error
      videoEl.onerror = function() {
        console.warn('Video failed to load:', videoPath);
        videoEl.style.display = 'none';
        videoPlaceholder.style.display = 'flex';
      };

      // Create the Footer_Italics box immediately
      const footerItalicsBox = createFooterItalicsBox();

      // Get data from sessionStorage
      let address = sessionStorage.getItem('veritas_address');
      let rawTextJson = sessionStorage.getItem('veritas_text_json');

      // If no data in sessionStorage, use the global ANALYSIS_DATA
      if (!rawTextJson) {
        console.log('No sessionStorage data found, using global ANALYSIS_DATA...');
        
        if (window.ANALYSIS_DATA) {
          rawTextJson = JSON.stringify(window.ANALYSIS_DATA);
          
          // Use default address if none provided
          if (!address) {
            address = "88 King Street, Unit 116, San Francisco 94107"; // Default to the legitimate address
          }
          
          console.log('Successfully loaded global ANALYSIS_DATA');
        } else {
          console.error('Global ANALYSIS_DATA not found');
          await renderFallbackContent('🔎 Searching Public Web Records', 'No data file provided.');
          return;
        }
      }

      // Parse JSON data
      let dict;
      try {
        dict = JSON.parse(rawTextJson);
      } catch (e) {
        console.error('JSON parsing error:', e);
        await renderFallbackContent('🔎 Searching Public Web Records', 'Text file is not valid JSON.');
        return;
      }

      // Find entry for address
      let entry = dict[address];
      
      // Fallback to default address if no match found
      if (!entry) {
        const defaultAddress = "88 King Street, Unit 116, San Francisco 94107";
        entry = dict[defaultAddress];
        
        if (!entry) {
          await renderFallbackContent(
            '🔎 Searching Public Web Records', 
            `No matching entry for "${address || 'Unknown Address'}".`
          );
          return;
        }
      }

      // Set up the 10-second timer to update the Footer_Italics box
      setTimeout(async () => {
        if (entry.footer_italics) {
          await updateFooterItalicsBox(footerItalicsBox, entry.footer_italics);
        }
      }, 6000); // 10 seconds

      // Render the streaming content
      await renderStreamForAddress(entry);

      // Wait a bit then redirect
      await wait(10000);
      window.location.href = 'results.html';

    } catch (error) {
      console.error('Loading page error:', error);
      await renderFallbackContent('🔎 Searching Public Web Records', 'An error occurred while loading data.');
    }
  }

  // Start the main function when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
  } else {
    main();
  }
})();
