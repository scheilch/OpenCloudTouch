import { getDeviceImage, getDeviceDisplayName, getDeviceAspectRatio } from "../utils/deviceImages";

/**
 * DeviceImage Component
 * Renders device product image with proper aspect ratio and fallback
 */

type SizeOption = "small" | "medium" | "large" | "full";

interface DeviceImageProps {
  deviceType?: string | null;
  alt?: string;
  className?: string;
  showLabel?: boolean;
  size?: SizeOption;
}

export default function DeviceImage({
  deviceType,
  alt,
  className = "",
  showLabel = false,
  size = "medium",
}: DeviceImageProps) {
  const imagePath = getDeviceImage(deviceType);
  const displayName = getDeviceDisplayName(deviceType);
  const aspectRatio = getDeviceAspectRatio(deviceType);

  const sizeClasses: Record<SizeOption, string> = {
    small: "w-16 h-16",
    medium: "w-32 h-32",
    large: "w-48 h-48",
    full: "w-full h-auto",
  };

  return (
    <div className={`device-image-container ${className}`}>
      <div className={`${sizeClasses[size]} ${aspectRatio} flex items-center justify-center`}>
        <img
          src={imagePath}
          alt={alt || displayName}
          className="w-full h-full object-contain"
          loading="lazy"
          onError={(e) => {
            // Fallback to default image on error
            const target = e.target as HTMLImageElement;
            if (target.src !== "/images/devices/default.svg") {
              target.src = "/images/devices/default.svg";
            }
          }}
        />
      </div>
      {showLabel && <div className="mt-2 text-center text-sm text-gray-400">{displayName}</div>}
    </div>
  );
}
