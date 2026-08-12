export const SkeletonCard = () => (
  <div className="bg-white rounded-lg border border-slate-200 p-5 shadow-sm animate-pulse">
    <div className="flex items-center justify-between mb-4">
      <div className="h-5 bg-slate-200 rounded w-1/3"></div>
      <div className="h-6 w-20 bg-slate-200 rounded-full"></div>
    </div>
    <div className="space-y-3">
      <div className="flex justify-between">
        <div className="h-4 bg-slate-200 rounded w-1/4"></div>
        <div className="h-4 bg-slate-200 rounded w-1/2"></div>
      </div>
      <div className="flex justify-between">
        <div className="h-4 bg-slate-200 rounded w-1/4"></div>
        <div className="h-4 bg-slate-200 rounded w-1/3"></div>
      </div>
    </div>
  </div>
);

export const SkeletonFeed = () => (
  <div className="space-y-4">
    {[1, 2, 3, 4, 5].map((i) => (
      <div key={i} className="flex gap-4 animate-pulse">
        <div className="w-16 h-4 bg-slate-200 rounded flex-shrink-0 mt-1"></div>
        <div className="flex-1 space-y-2">
          <div className="h-4 bg-slate-200 rounded w-3/4"></div>
          <div className="h-3 bg-slate-200 rounded w-1/2"></div>
        </div>
      </div>
    ))}
  </div>
);

export const SkeletonTable = () => (
  <div className="border border-slate-200 rounded-lg overflow-hidden animate-pulse">
    <div className="bg-slate-50 border-b border-slate-200 px-6 py-3">
      <div className="h-4 bg-slate-200 rounded w-1/4"></div>
    </div>
    <div className="divide-y divide-slate-100">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="px-6 py-4 flex items-center justify-between">
          <div className="space-y-2 w-1/2">
            <div className="h-4 bg-slate-200 rounded w-1/2"></div>
            <div className="h-3 bg-slate-200 rounded w-1/3"></div>
          </div>
          <div className="h-8 w-24 bg-slate-200 rounded"></div>
        </div>
      ))}
    </div>
  </div>
);
