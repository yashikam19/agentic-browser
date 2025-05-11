function extractDOM(mmidCounter) {
    function isVisible(element) {
        if (!element) return false;
        const rect = element.getBoundingClientRect();
        // Skip zero-sized elements
        if (rect.width === 0 && rect.height === 0) return false;
        
        const style = window.getComputedStyle(element);
        if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') {
            return false;
        }
        
        // Check only direct parent for visibility (reduce computation)
        const parentStyle = window.getComputedStyle(element.parentElement || {});
        if (parentStyle.display === 'none' || parentStyle.visibility === 'hidden') {
            return false;
        }
        
        return true;
    }

    function isInteractive(element) {
        if (!element) return false;
        const tag = element.tagName.toLowerCase();
        // Check only common interactive elements
        if (['a', 'button', 'input', 'textarea', 'select'].includes(tag)) return true;
        
        // Check only high-priority interactive roles
        const role = element.getAttribute('role');
        const interactiveRoles = ['button', 'link', 'checkbox', 'radio', 'textbox', 'searchbox'];
        if (role && interactiveRoles.includes(role)) return true;

        // Check tabIndex only as last resort
        const tabIndex = element.getAttribute('tabindex');
        if (tabIndex && parseInt(tabIndex) >= 0) return true;

        return false;
    }

    function shouldIncludeElement(element) {
        if (!element || !element.tagName) return false;
        
        const tag = element.tagName.toLowerCase();
        // Skip all non-visible, non-interactive elements
        if (!isVisible(element) && !isInteractive(element)) return false;
        
        // Always skip these elements
        if (['script', 'style', 'noscript', 'meta', 'link', 'path', 'svg', 'footer'].includes(tag)) {
            return false;
        }
        
        // Skip elements with no text and no interactive children unless they are interactive
        const text = element.textContent.trim();
        if (!text && !isInteractive(element) && !element.querySelector('a, button, input, textarea, select')) {
            return false;
        }
        
        // Skip very deeply nested elements that aren't interactive
        if (!isInteractive(element)) {
            let depth = 0;
            let parent = element.parentElement;
            while (parent && depth < 8) {
                depth++;
                parent = parent.parentElement;
            }
            if (depth >= 8) return false;
        }
        
        return true;
    }

    function getElementText(element) {
        if (!element) return '';
        if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
            return element.getAttribute('placeholder') || 
                   element.getAttribute('aria-label') || 
                   element.value || '';
        }
        if (element.tagName === 'IMG') return element.getAttribute('alt') || '';
        
        let text = element.textContent.trim();
        text = text.replace(/\s+/g, ' ');
        // Limit text length even more to save tokens
        return text.length > 50 ? text.substring(0, 50) + '...' : text;
    }

    function extractElementInfo(element, counter) {
        if (!shouldIncludeElement(element)) return null;
        
        const tag = element.tagName.toLowerCase();
        
        // Assign mmid and set it as an attribute
        const mmid = String(counter.count++);
        element.setAttribute('mmid', mmid);

        const info = { 
            mmid: mmid,
            tag: tag
        };
        
        // Only include interactive property if true
        if (isInteractive(element)) info.interactive = true;
        
        // Get element text only if it's likely important
        const text = getElementText(element);
        if (text) info.name = text;
        
        // Include only the most important attributes
        if (tag === 'input') {
            info.input_type = element.type;
            // Only include value if the input type is not password
            if (element.value && element.type !== 'password') info.value = element.value;
        }

        // Limit attributes to the most critical ones
        const criticalAttrs = ['id', 'aria-label', 'placeholder', 'href'];
        criticalAttrs.forEach(attr => {
            const value = element.getAttribute(attr);
            if (value && value.length < 50) info[attr] = value;
        });

        // Include focused state as it's important for navigation
        if (document.activeElement === element) info.focused = true;

        return info;
    }

    // Use a more efficient DOM traversal approach
    function processElements() {
        const result = [];
        const counter = { count: mmidCounter || 1 };
        
        // Function to process an element and its children
        function processElement(element) {
            const info = extractElementInfo(element, counter);
            if (info) result.push(info);
            
            // Skip processing children of certain elements to save tokens
            const tag = element.tagName.toLowerCase();
            if (['svg', 'iframe', 'canvas'].includes(tag)) return;
            
            // Process children
            for (const child of element.children) {
                processElement(child);
            }
        }
        
        // Process from body to avoid head elements
        if (document.body) processElement(document.body);
        
        return {
            role: 'WebArea',
            name: document.title,
            children: result,
            mmid_counter: counter.count
        };
    }

    return processElements();
}