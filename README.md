# redainess
Publica presentacion de la plataforma



## 🛠️ Tech Stack

* **Framework:** Next.js 14 (App Router)
* **Styling:** TailwindCSS
* **Component Libraries:** React Icons, Framer Motion
* **Data Simulation:** JSON file via `/api/data` route

---

## 🧩 Simulated Backend (`/api/data`)

The JSON returned mimics MongoDB collections:

* `product`: Product ID and names
* `additive`: Pigment names and capabilities
* `kg_sbe_pigm`, `car_per_kg`: Relationships for conversion
* `schedule`: Weekly product demands
* `formula_pallet_fact`: Factors for pallet planning
* `sack_per_pallet`: Sack replenishment multipliers
* `mix_per_week`: Additive mix values for weekly inventory
* `set_parameters`: Global settings (year, assumptions, capacity)

> **Optional:** Simulated `/api/schedule/[id]` PUT route for in-place editing (non-persistent)

---

## 🧪 Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# View app at http://localhost:3000
```

### 🔄 Build & Production (PM2 Example)

```bash
# Build the app
npm run build

# Start in production mode
npm start

# Or using pm2
pm2 serve ./.next 3000 --spa --name tecnoboyer-dashboard
```

---

## 📂 Project Layout (Simplified)

```
app/
  dashboard/            # Dashboard views
  services/             # Educational walkthroughs
  about/                # Experience + contact
  api/data/route.ts     # Simulated JSON backend
components/             # Reusable visual modules
public/                 # Logos, icons, assets
```

