import React from 'react';
import { Landmark } from '../api';

interface SkeletonViewerProps {
  landmarks: Landmark[];
  affectedSide?: 'Left' | 'Right' | 'Bilateral';
}

export const SkeletonViewer: React.FC<SkeletonViewerProps> = ({ landmarks, affectedSide = 'Right' }) => {
  if (!landmarks || landmarks.length === 0) {
    return (
      <div className="w-full h-80 bg-slate-900 border border-slate-800 rounded-2xl flex items-center justify-center text-slate-500 font-medium">
        No skeleton landmarks loaded
      </div>
    );
  }

  // standard connection pairings in MediaPipe Pose
  const connections = [
    [11, 12], // shoulders
    [11, 13], [13, 15], // left arm
    [12, 14], [14, 16], // right arm
    [11, 23], [12, 24], // shoulders to hips
    [23, 24], // hips
    [23, 25], [25, 27], // left leg
    [24, 26], [26, 28], // right leg
    [27, 29], [29, 31], [27, 31], // left foot
    [28, 30], [30, 32], [28, 32], // right foot
  ];

  // Helper to determine line color based on affected side
  const getLineColor = (idA: number, idB: number) => {
    const isLeftLimb = [11, 13, 15, 23, 25, 27, 29, 31].includes(idA) && [11, 13, 15, 23, 25, 27, 29, 31].includes(idB);
    const isRightLimb = [12, 14, 16, 24, 26, 28, 30, 32].includes(idA) && [12, 14, 16, 24, 26, 28, 30, 32].includes(idB);

    if (affectedSide === 'Left' && isLeftLimb) {
      return '#EF4444'; // Red for affected limb
    }
    if (affectedSide === 'Right' && isRightLimb) {
      return '#EF4444'; // Red for affected limb
    }
    return '#14B8A6'; // Teal for healthy/unaffected limbs
  };

  return (
    <div className="relative w-full aspect-video bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 shadow-2xl flex items-center justify-center">
      {/* Background medical grid */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#020617_1px,transparent_1px),linear-gradient(to_bottom,#020617_1px,transparent_1px)] bg-[size:4%_6%] opacity-40"></div>
      
      <svg 
        viewBox="0 0 1 1" 
        className="w-full h-full absolute"
      >
        {/* Draw connections */}
        {connections.map(([idA, idB], index) => {
          const ptA = landmarks.find(lm => lm.id === idA);
          const ptB = landmarks.find(lm => lm.id === idB);
          
          if (!ptA || !ptB) return null;
          
          const strokeColor = getLineColor(idA, idB);
          
          return (
            <line
              key={`line-${index}`}
              x1={ptA.x}
              y1={ptA.y}
              x2={ptB.x}
              y2={ptB.y}
              stroke={strokeColor}
              strokeWidth="0.006"
              className="skeleton-line"
              style={{
                filter: `drop-shadow(0 0 4px ${strokeColor})`,
                opacity: (ptA.visibility > 0.4 && ptB.visibility > 0.4) ? 0.9 : 0.2
              }}
            />
          );
        })}

        {/* Draw joints */}
        {landmarks.map((lm) => {
          const isLeft = [11, 13, 15, 23, 25, 27, 29, 31].includes(lm.id);
          const isRight = [12, 14, 16, 24, 26, 28, 30, 32].includes(lm.id);
          
          let color = '#2563EB'; // Blue default
          if (affectedSide === 'Left' && isLeft) color = '#EF4444';
          else if (affectedSide === 'Right' && isRight) color = '#EF4444';
          else if (isLeft || isRight) color = '#14B8A6'; // Teal

          // Skip face points 1-10 to make skeleton cleaner (nose/eyes clutter walk overlays)
          if (lm.id > 0 && lm.id < 11) return null;

          return (
            <circle
              key={`joint-${lm.id}`}
              cx={lm.x}
              cy={lm.y}
              r={lm.id === 0 ? "0.012" : "0.008"} // Head is slightly larger
              fill={color}
              stroke="#FFF"
              strokeWidth="0.002"
              style={{
                filter: `drop-shadow(0 0 3px ${color})`,
                opacity: lm.visibility > 0.4 ? 1 : 0.1
              }}
            />
          );
        })}
      </svg>

      {/* Floating Legend */}
      <div className="absolute bottom-4 right-4 bg-slate-900/90 backdrop-blur-md px-3.5 py-2.5 rounded-xl border border-slate-800 text-[10px] space-y-1.5 shadow-xl text-white">
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#14B8A6] border border-white/20"></div>
          <span className="font-semibold text-slate-300">Healthy Side</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#EF4444] border border-white/20"></div>
          <span className="font-semibold text-slate-300">Hemiparetic Affected Side ({affectedSide})</span>
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-2.5 h-2.5 rounded-full bg-[#2563EB] border border-white/20"></div>
          <span className="font-semibold text-slate-300">Center Core Nodes</span>
        </div>
      </div>
    </div>
  );
};
export default SkeletonViewer;
