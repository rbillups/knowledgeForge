import type { KnowledgeCollection } from "@/types/dashboard";

type RecentCollectionsProps = {
  collections: KnowledgeCollection[];
};

export function RecentCollections({ collections }: RecentCollectionsProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 px-5 py-4">
        <h2 className="text-base font-semibold text-slate-900">
          Recent knowledge collections
        </h2>
        <p className="mt-0.5 text-sm text-slate-500">
          Collections updated most recently across your organization
        </p>
      </div>
      <ul className="divide-y divide-slate-100">
        {collections.map((collection) => (
          <li
            key={collection.id}
            className="flex items-center justify-between px-5 py-4 transition-colors hover:bg-slate-50"
          >
            <div>
              <p className="text-sm font-medium text-slate-900">
                {collection.name}
              </p>
              <p className="mt-0.5 text-sm text-slate-500">
                {collection.owner} · {collection.documentCount} documents
              </p>
            </div>
            <span className="text-xs text-slate-400">
              {collection.lastUpdated}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
