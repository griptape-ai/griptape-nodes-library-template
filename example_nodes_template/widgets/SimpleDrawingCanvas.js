/**
 * SimpleDrawingCanvas - Minimal canvas widget demonstrating retina scaling and cleanup.
 * Users can draw with their pointer and clear the canvas.
 */

const WIDGET_VERSION = "0.1.0";

export default function SimpleDrawingCanvas(container, props) {
  const { value, onChange, disabled } = props;

  const CANVAS_HEIGHT = 300;
  const dpr = window.devicePixelRatio || 1;

  let isDrawing = false;
  let lastX = 0;
  let lastY = 0;
  let lastBaseImage = value?.baseImage || null;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  // Canvas styling
  canvas.style.width = '100%';
  canvas.style.height = CANVAS_HEIGHT + 'px';
  canvas.style.background = '#1a1a1a';
  canvas.style.cursor = disabled ? 'default' : 'crosshair';
  canvas.style.display = 'block';
  canvas.className = 'nodrag nowheel';

  // Drawing settings
  ctx.strokeStyle = '#3b82f6';
  ctx.lineWidth = 3;
  ctx.lineCap = 'round';
  ctx.lineJoin = 'round';

  function setupCanvas() {
    // Get the actual rendered CSS size
    const canvasWidth = canvas.offsetWidth;
    const canvasHeight = canvas.offsetHeight;

    // Set canvas internal resolution for retina
    canvas.width = canvasWidth * dpr;
    canvas.height = canvasHeight * dpr;
    ctx.scale(dpr, dpr);

    // Reapply drawing settings
    ctx.strokeStyle = '#3b82f6';
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    console.log('[SimpleDrawingCanvas] setupCanvas called', {
      hasBaseImage: !!(value && value.baseImage),
      hasImageData: !!(value && value.imageData),
      baseImage: value?.baseImage?.substring(0, 50)
    });

    // Load base image if provided (for annotation)
    if (value && value.baseImage) {
      const baseImg = new Image();
      baseImg.crossOrigin = 'anonymous';
      baseImg.onload = () => {
        console.log('[SimpleDrawingCanvas] Base image loaded successfully');
        // Draw base image
        ctx.drawImage(baseImg, 0, 0, canvasWidth, canvasHeight);

        // Load existing drawing on top if present and not empty
        if (value.imageData && value.imageData !== "") {
          const drawingImg = new Image();
          drawingImg.onload = () => ctx.drawImage(drawingImg, 0, 0, canvasWidth, canvasHeight);
          drawingImg.src = value.imageData;
        }
      };
      baseImg.onerror = (e) => {
        console.error('[SimpleDrawingCanvas] Failed to load base image:', e);
      };
      baseImg.src = value.baseImage;
    } else if (value && value.imageData && value.imageData !== "") {
      // Just load existing drawing if no base image
      const img = new Image();
      img.onload = () => ctx.drawImage(img, 0, 0, canvasWidth, canvasHeight);
      img.src = value.imageData;
    }
  }

  function startDrawing(e) {
    if (disabled) return;
    isDrawing = true;
    lastX = e.offsetX;
    lastY = e.offsetY;
  }

  function draw(e) {
    if (!isDrawing || disabled) return;
    const x = e.offsetX;
    const y = e.offsetY;

    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x, y);
    ctx.stroke();

    lastX = x;
    lastY = y;
  }

  function stopDrawing() {
    if (!isDrawing) return;
    isDrawing = false;
    emitChange();
  }

  function emitChange() {
    if (disabled || !onChange) return;
    const imageData = canvas.toDataURL('image/png');
    const result = { imageData };
    // Preserve base image reference
    if (value && value.baseImage) {
      result.baseImage = value.baseImage;
    }
    onChange(result);
  }

  function clearCanvas() {
    const canvasWidth = canvas.offsetWidth;
    const canvasHeight = canvas.offsetHeight;

    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    // Redraw base image if present and emit with empty imageData
    if (value && value.baseImage) {
      const baseImg = new Image();
      baseImg.onload = () => {
        ctx.drawImage(baseImg, 0, 0, canvasWidth, canvasHeight);
        // Clear annotations by setting imageData to empty
        const result = { imageData: "", baseImage: value.baseImage };
        onChange(result);
      };
      baseImg.src = value.baseImage;
    } else {
      // No base image, just clear everything
      onChange({ imageData: "" });
    }
  }

  // Event listeners
  canvas.addEventListener('pointerdown', startDrawing);
  canvas.addEventListener('pointermove', draw);
  canvas.addEventListener('pointerup', stopDrawing);
  canvas.addEventListener('pointerleave', stopDrawing);

  // Canvas container with border
  const canvasContainer = document.createElement('div');
  canvasContainer.style.cssText = `
    border: 2px solid #444;
    border-radius: 6px;
    overflow: hidden;
  `;
  canvasContainer.appendChild(canvas);

  // Build UI
  const wrapper = document.createElement('div');
  wrapper.style.cssText = `
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding: 12px;
    background: #0a0a0a;
    border-radius: 6px;
  `;

  const clearBtn = document.createElement('button');
  clearBtn.textContent = 'Clear';
  clearBtn.disabled = disabled;
  clearBtn.style.cssText = `
    padding: 6px 12px;
    background: #c44;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: ${disabled ? 'default' : 'pointer'};
    font-size: 12px;
    transition: background 0.2s;
  `;
  if (!disabled) {
    clearBtn.addEventListener('pointerenter', () => clearBtn.style.background = '#d55');
    clearBtn.addEventListener('pointerleave', () => clearBtn.style.background = '#c44');
    clearBtn.addEventListener('pointerdown', (e) => {
      e.stopPropagation();
      clearCanvas();
    });
  }

  wrapper.appendChild(canvasContainer);
  wrapper.appendChild(clearBtn);
  container.appendChild(wrapper);

  // Setup canvas after it's in the DOM
  setupCanvas();

  // Watch for value changes (e.g., when base image is added)
  const checkForUpdates = setInterval(() => {
    const currentBaseImage = value?.baseImage || null;
    if (currentBaseImage !== lastBaseImage) {
      lastBaseImage = currentBaseImage;
      setupCanvas();
    }
  }, 100);

  // Cleanup function
  return () => {
    clearInterval(checkForUpdates);
    canvas.removeEventListener('pointerdown', startDrawing);
    canvas.removeEventListener('pointermove', draw);
    canvas.removeEventListener('pointerup', stopDrawing);
    canvas.removeEventListener('pointerleave', stopDrawing);
  };
}
