import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

export default async function Home({ searchParams }: { searchParams: { season?: string } }) {
  // 1. Fetch filtered data from Supabase
  let query = supabase.from('products').select('*')
  
  if (searchParams.season) {
    query = query.eq('color_season', searchParams.season)
  }

  const { data: products } = await query

  return (
    <main className="min-h-screen bg-white p-8">
      <header className="mb-12 text-center">
        <h1 className="text-4xl font-serif mb-4 uppercase tracking-widest">Color Match Collective</h1>
        <p className="text-gray-500 italic">Curated luxury for your specific palette.</p>
      </header>

      {/* Season Filter Bar */}
      <nav className="flex justify-center gap-4 mb-12 flex-wrap">
        {['Deep Winter', 'Cool Summer', 'Warm Autumn', 'Bright Spring'].map((s) => (
          <a 
            href={`/?season=${s}`} 
            key={s}
            className="px-6 py-2 border border-black hover:bg-black hover:text-white transition-all text-sm uppercase"
          >
            {s}
          </a>
        ))}
      </nav>

      {/* Product Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-8">
        {products?.map((item) => (
          <div key={item.id} className="group cursor-pointer">
            <div className="relative aspect-[3/4] overflow-hidden bg-gray-100">
              <img 
                src={item.image_url} 
                alt={item.product_name}
                className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500"
              />
              <div className="absolute top-2 right-2 bg-white/90 px-2 py-1 text-[10px] uppercase font-bold">
                {item.color_season}
              </div>
            </div>
            <h3 className="mt-4 text-sm font-medium">{item.product_name}</h3>
            <p className="text-gray-500 text-xs uppercase tracking-tighter">{item.store_name} • {item.price}</p>
          </div>
        ))}
      </div>
    </main>
  )
}