interface DraggableImage {
  element: HTMLElement;
  isDragging: boolean;
  startX: number;
  startY: number;
  currentX: number;
  currentY: number;
  imageData: ImageData | null;
  canvas: HTMLCanvasElement;
}

class ProjectorEffect {
  private images: DraggableImage[] = [];
  private container: HTMLElement;
  private blendOverlays: HTMLCanvasElement[] = []; // Array of canvas overlays
  private lastDraggedImage: DraggableImage | null = null; // Track most recently dragged image

  constructor(containerId: string) {
    this.container = document.getElementById(containerId)!;
    this.init().catch(console.error);;
  }

  private createBlendOverlay(): HTMLCanvasElement {
    const canvas = document.createElement('canvas');
    canvas.style.position = 'absolute';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '10';
    canvas.style.display = 'none';
    this.container.appendChild(canvas);
    return canvas;
  }

  private async init(): Promise<void> {
    await this.setupImages();
    this.addEventListeners();
  }

  private async setupImages(): Promise<void> {
    const imageElements = this.container.querySelectorAll('.draggable-image') as NodeListOf<HTMLElement>;
    
    for (let index = 0; index < imageElements.length; index++) {
      const img = imageElements[index];
      const canvas = document.createElement('canvas');
      canvas.width = 350;
      canvas.height = 350;
      
      const draggableImage: DraggableImage = {
        element: img,
        isDragging: false,
        startX: 0,
        startY: 0,
        currentX: index * 500,
        currentY: 100,
        imageData: null,
        canvas: canvas
      };

      img.style.position = 'absolute';
      img.style.left = `${draggableImage.currentX}px`;
      img.style.top = `${draggableImage.currentY}px`;
      img.style.cursor = 'grab';

      // Load the image data
      await this.loadImageData(draggableImage);
      this.images.push(draggableImage);
    }
  }

  private async loadImageData(draggableImage: DraggableImage): Promise<void> {
    const bgImage = window.getComputedStyle(draggableImage.element).backgroundImage;
    const urlMatch = bgImage.match(/url\(["']?([^"']+)["']?\)/);
    
    if (urlMatch) {
      const imageUrl = urlMatch[1];
      try {
        const img = new Image();
        img.crossOrigin = 'anonymous';
        
        await new Promise((resolve, reject) => {
          img.onload = resolve;
          img.onerror = reject;
          img.src = imageUrl;
        });

        const ctx = draggableImage.canvas.getContext('2d')!;
        ctx.drawImage(img, 0, 0, 350, 350);
        draggableImage.imageData = ctx.getImageData(0, 0, 350, 350);
      } catch (error) {
        console.warn('Could not load image:', imageUrl);
      }
    }
  }

  private addEventListeners(): void {
    this.images.forEach(img => {
      img.element.addEventListener('mousedown', (e) => this.startDrag(e, img));
    });

    document.addEventListener('mousemove', (e) => this.drag(e));
    document.addEventListener('mouseup', () => this.stopDrag());
    document.addEventListener('keydown', (e) => this.handleKeyPress(e));
  }

  private startDrag(e: MouseEvent, img: DraggableImage): void {
    img.isDragging = true;
    img.startX = e.clientX - img.currentX;
    img.startY = e.clientY - img.currentY;
    img.element.style.cursor = 'grabbing';
    this.lastDraggedImage = img;
    e.preventDefault();
  }

  private drag(e: MouseEvent): void {
    this.images.forEach(img => {
      if (img.isDragging) {
        img.currentX = e.clientX - img.startX;
        img.currentY = e.clientY - img.startY;
        
        img.element.style.left = `${img.currentX}px`;
        img.element.style.top = `${img.currentY}px`;
        
        this.checkOverlap();
      }
    });
  }

  private stopDrag(): void {
    this.images.forEach(img => {
      img.isDragging = false;
      img.element.style.cursor = 'grab';
    });
  }

  
  private handleKeyPress(e: KeyboardEvent): void {
    if (!this.lastDraggedImage) return;

    const nudgeAmount = 1; // Pixels to move per key press
    let moved = false;

    switch (e.key) {
      case 'ArrowUp':
        this.lastDraggedImage.currentY -= nudgeAmount;
        moved = true;
        break;
      case 'ArrowDown':
        this.lastDraggedImage.currentY += nudgeAmount;
        moved = true;
        break;
      case 'ArrowLeft':
        this.lastDraggedImage.currentX -= nudgeAmount;
        moved = true;
        break;
      case 'ArrowRight':
        this.lastDraggedImage.currentX += nudgeAmount;
        moved = true;
        break;
    }

    if (moved) {
      // Update the element position
      this.lastDraggedImage.element.style.left = `${this.lastDraggedImage.currentX}px`;
      this.lastDraggedImage.element.style.top = `${this.lastDraggedImage.currentY}px`;
      
      // Check for overlaps after nudging
      this.checkOverlap();
      
      // Prevent default arrow key behavior (like scrolling)
      e.preventDefault();
    }
  }

  private checkOverlap(): void {
    this.hideAllBlendOverlays();
    
    let overlayIndex = 0;
    
    for (let i = 0; i < this.images.length; i++) {
      for (let j = i + 1; j < this.images.length; j++) {
        const img1 = this.images[i];
        const img2 = this.images[j];
        
        const overlap = this.calculateOverlap(img1, img2);
        if (overlap.isOverlapping && overlap.overlapArea && img1.imageData && img2.imageData) {
          if (overlayIndex >= this.blendOverlays.length) {
            this.blendOverlays.push(this.createBlendOverlay());
          }
          
          this.showPixelBlendedImage(
            this.blendOverlays[overlayIndex], 
            overlap.overlapArea, 
            img1, 
            img2
          );
          overlayIndex++;
        }
      }
    }
  }
  private showPixelBlendedImage(canvas: HTMLCanvasElement, overlapArea: any, img1: DraggableImage, img2: DraggableImage): void {
    const containerRect = this.container.getBoundingClientRect();
    
    const width = Math.floor(overlapArea.right - overlapArea.left);
    const height = Math.floor(overlapArea.bottom - overlapArea.top);
    
    // Check if overlap area is valid (has actual area and is a valid number)
    if (!width || !height || width <= 0 || height <= 0 || !Number.isFinite(width) || !Number.isFinite(height)) {
      canvas.style.display = 'none';
      return;
    }
    
    canvas.style.display = 'block';
    canvas.style.left = `${overlapArea.left - containerRect.left}px`;
    canvas.style.top = `${overlapArea.top - containerRect.top}px`;
    
    canvas.width = width;
    canvas.height = height;
    
    const ctx = canvas.getContext('2d')!;
    const blendedImageData = ctx.createImageData(width, height);

    // Calculate relative positions within each image
    const img1Rect = img1.element.getBoundingClientRect();
    const img2Rect = img2.element.getBoundingClientRect();
    
    const img1OffsetX = overlapArea.left - img1Rect.left;
    const img2OffsetX = overlapArea.left - img2Rect.left;
    const img1OffsetY = overlapArea.top - img1Rect.top;
    const img2OffsetY = overlapArea.top - img2Rect.top;
    
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const outputIndex = (y * width + x) * 4;
        
        // Get pixel from each image
        const img1X = Math.floor(img1OffsetX + x);
        const img1Y = Math.floor(img1OffsetY + y);
        const img2X = Math.floor(img2OffsetX + x);
        const img2Y = Math.floor(img2OffsetY + y);
        
        const img1Index = (img1Y * 350 + img1X) * 4;
        const img2Index = (img2Y * 350 + img2X) * 4;
        
        // Get RGBA values (with bounds checking)
        const r1 = (img1Index >= 0 && img1Index < img1.imageData!.data.length) ? img1.imageData!.data[img1Index] : 0;
        const g1 = (img1Index >= 0 && img1Index < img1.imageData!.data.length) ? img1.imageData!.data[img1Index + 1] : 0;
        const b1 = (img1Index >= 0 && img1Index < img1.imageData!.data.length) ? img1.imageData!.data[img1Index + 2] : 0;
        const a1 = (img1Index >= 0 && img1Index < img1.imageData!.data.length) ? img1.imageData!.data[img1Index + 3] : 0;
        
        const r2 = (img2Index >= 0 && img2Index < img2.imageData!.data.length) ? img2.imageData!.data[img2Index] : 0;
        const g2 = (img2Index >= 0 && img2Index < img2.imageData!.data.length) ? img2.imageData!.data[img2Index + 1] : 0;
        const b2 = (img2Index >= 0 && img2Index < img2.imageData!.data.length) ? img2.imageData!.data[img2Index + 2] : 0;
        const a2 = (img2Index >= 0 && img2Index < img2.imageData!.data.length) ? img2.imageData!.data[img2Index + 3] : 0;
        
        // Multiplicative blending (like light filters)
        const blendedR = Math.round((r1 / 255) * (r2 / 255) * 255);
        const blendedG = Math.round((g1 / 255) * (g2 / 255) * 255);
        const blendedB = Math.round((b1 / 255) * (b2 / 255) * 255);
        const blendedA = Math.max(a1, a2); // Use the maximum alpha
        
        blendedImageData.data[outputIndex] = blendedR;
        blendedImageData.data[outputIndex + 1] = blendedG;
        blendedImageData.data[outputIndex + 2] = blendedB;
        blendedImageData.data[outputIndex + 3] = blendedA;
      }
    }
    
    ctx.putImageData(blendedImageData, 0, 0);
  }

  private hideAllBlendOverlays(): void {
    this.blendOverlays.forEach(overlay => {
      overlay.style.display = 'none';
    });
  }

  private calculateOverlap(img1: DraggableImage, img2: DraggableImage) {
    const rect1 = img1.element.getBoundingClientRect();
    const rect2 = img2.element.getBoundingClientRect();

    const isOverlapping = !(
      rect1.right < rect2.left ||
      rect1.left > rect2.right ||
      rect1.bottom < rect2.top ||
      rect1.top > rect2.bottom
    );

    return {
      isOverlapping,
      overlapArea: isOverlapping ? {
        left: Math.max(rect1.left, rect2.left),
        right: Math.min(rect1.right, rect2.right),
        top: Math.max(rect1.top, rect2.top),
        bottom: Math.min(rect1.bottom, rect2.bottom)
      } : null
    };
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  new ProjectorEffect('projector-container');
});