import type { Village } from '../../types/village';

interface VillageInfoProps {
  village: Village;
}

export default function VillageInfo({ village }: VillageInfoProps) {
  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h3 className="font-semibold text-gray-900">{village.name}</h3>
        <p className="text-sm text-gray-600 mt-1">
          {village.taluk} Taluk, {village.district} District
        </p>
      </div>

      <div className="p-4 space-y-4">
        {/* Key Metrics */}
        <div>
          <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
            Key Metrics
          </h4>
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-blue-50 p-3 rounded-lg">
              <div className="text-2xl font-bold text-blue-900">
                {village.estimated_households}
              </div>
              <div className="text-xs text-blue-700 mt-1">Households</div>
            </div>
            <div className="bg-green-50 p-3 rounded-lg">
              <div className="text-2xl font-bold text-green-900">
                {village.estimated_population}
              </div>
              <div className="text-xs text-green-700 mt-1">Population</div>
            </div>
          </div>
        </div>

        {/* Area */}
        <div>
          <div className="flex items-center justify-between py-2 border-b">
            <span className="text-sm text-gray-600">Area</span>
            <span className="text-sm font-medium text-gray-900">
              {village.area_sq_km} km²
            </span>
          </div>
        </div>

        {/* Priority Infrastructure */}
        {village.priority_infrastructure && village.priority_infrastructure.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
              Priority Infrastructure
            </h4>
            <div className="flex flex-wrap gap-2">
              {village.priority_infrastructure.map((infra) => (
                <span
                  key={infra}
                  className="px-3 py-1 bg-amber-100 text-amber-800 text-xs rounded-full"
                >
                  {infra}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Description */}
        {village.description && (
          <div>
            <h4 className="text-xs font-semibold text-gray-500 uppercase mb-2">
              Description
            </h4>
            <p className="text-sm text-gray-700">{village.description}</p>
          </div>
        )}


      </div>
    </div>
  );
}
