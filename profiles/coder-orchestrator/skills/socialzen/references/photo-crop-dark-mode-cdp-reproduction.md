# Photo crop dark-mode CDP reproduction

Use when the user reports a Photo Crop modal bug that persists after deploy/hard refresh and explicitly asks not to guess.

## Read-only reproduction path

1. Start a local/headless Chromium with CDP against the already-served SocialZen app:
   ```bash
   chromium-browser --headless=new --remote-debugging-port=9222 --disable-gpu --no-sandbox --user-data-dir=/tmp/socialzen-chrome about:blank
   ```
2. Open `/projects/socialzen/app/posts/new`, sign in with the local/demo account if needed, then force dark mode in the page before uploading:
   ```js
   document.documentElement.classList.add('dark')
   localStorage.setItem('theme', 'dark')
   ```
3. For hidden React file inputs, `DOM.setFileInputFiles` may report success while `input.files.length` remains `0`. If that happens, inject a `File` through `DataTransfer` and dispatch a bubbling `change` event:
   ```js
   const bytes = Uint8Array.from(atob(BASE64_IMAGE), c => c.charCodeAt(0))
   const file = new File([bytes], 'crop-test.jpg', { type: 'image/jpeg' })
   const dt = new DataTransfer()
   dt.items.add(file)
   const input = document.querySelector('input[type=file]')
   Object.defineProperty(input, 'files', { value: dt.files, configurable: true })
   input.dispatchEvent(new Event('change', { bubbles: true }))
   ```
4. Wait for the crop modal image to have `naturalWidth > 0`, then capture:
   - full-page screenshot of the modal;
   - computed styles on the blob image: `filter`, `opacity`, `mixBlendMode`;
   - crop-surface dimensions/background;
   - crop box `left/top/width/height`.
5. Click the **modal footer Apply button** (not the custom-ratio Apply button):
   ```js
   [...[...document.querySelectorAll('button')].filter(b => b.textContent.trim() === 'Apply')].pop().click()
   ```
6. Capture the post media preview screenshot and image metadata (`naturalWidth`, `naturalHeight`, CSS filters). This separates modal rendering from generated/uploaded media output.

## Interpretation

- If the original blob image has real dimensions and the final media preview renders correctly, the first bad layer is the **crop modal rendering**, not upload, generated file, or banner/media preview.
- If the modal screenshot is dark/blank only under `.dark` while computed image styles are already `filter: none`, `opacity: 1`, and `mix-blend-mode: normal`, inspect Dark Mode selectors and parent/surface backgrounds before changing crop math.
- Always state which layer first becomes incorrect: original upload, crop modal, crop preview, generated cropped image, uploaded file, final preview.

## User-facing discipline

When prior crop fixes failed, do not propose another fix in the same response as reproduction unless the failing layer is proven. Return screenshots/logs/debug values first and wait for explicit implementation/deployment wording.