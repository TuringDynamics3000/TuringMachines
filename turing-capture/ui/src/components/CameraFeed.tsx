// TuringIdentity™ Camera Feed Component
// Live video feed with MediaPipe FaceMesh integration

import React, { useRef, useEffect, useState } from 'react';
import { FaceMesh, Results } from '@mediapipe/face_mesh';
import { Camera } from '@mediapipe/camera_utils';

interface CameraFeedProps {
  onResults: (results: Results) => void;
  onError?: (error: Error) => void;
  width?: number;
  height?: number;
  mirrored?: boolean;
}

export default function CameraFeed({
  onResults,
  onError,
  width = 480,
  height = 640,
  mirrored = true,
}: CameraFeedProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const faceMeshRef = useRef<FaceMesh | null>(null);
  const cameraRef = useRef<Camera | null>(null);

  useEffect(() => {
    let mounted = true;

    const initializeCamera = async () => {
      try {
        if (!videoRef.current) return;

        // Initialize MediaPipe FaceMesh
        const faceMesh = new FaceMesh({
          locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
          },
        });

        faceMesh.setOptions({
          maxNumFaces: 1,
          refineLandmarks: true,
          minDetectionConfidence: 0.6,
          minTrackingConfidence: 0.6,
        });

        faceMesh.onResults((results: Results) => {
          if (mounted) {
            onResults(results);
            
            // Draw results on canvas for visual feedback
            if (canvasRef.current && results.image) {
              const ctx = canvasRef.current.getContext('2d');
              if (ctx) {
                canvasRef.current.width = results.image.width;
                canvasRef.current.height = results.image.height;
                
                // Clear canvas
                ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
                
                // Draw the image
                ctx.save();
                if (mirrored) {
                  ctx.scale(-1, 1);
                  ctx.translate(-canvasRef.current.width, 0);
                }
                ctx.drawImage(results.image, 0, 0, canvasRef.current.width, canvasRef.current.height);
                ctx.restore();
              }
            }
          }
        });

        faceMeshRef.current = faceMesh;

        // Initialize camera
        const camera = new Camera(videoRef.current, {
          onFrame: async () => {
            if (videoRef.current && faceMeshRef.current) {
              await faceMeshRef.current.send({ image: videoRef.current });
            }
          },
          width,
          height,
        });

        cameraRef.current = camera;
        await camera.start();

        if (mounted) {
          setIsLoading(false);
        }
      } catch (err) {
        console.error('Camera initialization error:', err);
        const error = err instanceof Error ? err : new Error('Failed to initialize camera');
        if (mounted) {
          setError(error.message);
          setIsLoading(false);
        }
        if (onError) {
          onError(error);
        }
      }
    };

    initializeCamera();

    return () => {
      mounted = false;
      
      // Cleanup
      if (cameraRef.current) {
        cameraRef.current.stop();
      }
      
      if (faceMeshRef.current) {
        faceMeshRef.current.close();
      }
    };
  }, [onResults, onError, width, height, mirrored]);

  return (
    <div className="relative w-full h-full">
      {/* Hidden video element for MediaPipe */}
      <video
        ref={videoRef}
        className="hidden"
        autoPlay
        muted
        playsInline
      />

      {/* Canvas for rendering */}
      <canvas
        ref={canvasRef}
        className={`w-full h-full rounded-lg shadow-lg ${mirrored ? 'scale-x-[-1]' : ''}`}
        style={{ objectFit: 'cover' }}
      />

      {/* Loading overlay */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75 rounded-lg">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p className="text-white text-sm">Initializing camera...</p>
          </div>
        </div>
      )}

      {/* Error overlay */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-900 bg-opacity-75 rounded-lg">
          <div className="text-center px-4">
            <svg
              className="w-12 h-12 text-white mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <p className="text-white text-sm font-semibold mb-2">Camera Error</p>
            <p className="text-white text-xs">{error}</p>
            <p className="text-white text-xs mt-2">
              Please allow camera access and try again
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
