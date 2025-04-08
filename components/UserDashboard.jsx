import Link from 'next/link';

{/* Career Section */}
<div className="col-span-12 md:col-span-6 lg:col-span-4">
  <div className="card bg-base-100 shadow-lg h-full">
    <div className="card-body">
      <h2 className="card-title">Career</h2>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="font-medium">Enhanced Job Search</h3>
            <p className="text-sm text-base-content/70">Find climate jobs matching your skills</p>
          </div>
          <Link href="/jobs/enhanced-search" className="btn btn-primary btn-sm">
            Search
          </Link>
        </div>
        
        <div className="divider my-1"></div>
        
        <div className="flex justify-between items-center">
          <div>
            <h3 className="font-medium">Profile Enrichment</h3>
            <p className="text-sm text-base-content/70">Enhance your profile for better matches</p>
          </div>
          <Link href="/profile/enrich" className="btn btn-outline btn-sm">
            Enhance
          </Link>
        </div>
      </div>
    </div>
  </div>
</div> 