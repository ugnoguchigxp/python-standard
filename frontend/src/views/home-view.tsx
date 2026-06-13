export function HomeView() {
	return (
		<main className="home-shell">
			<section className="home-panel">
				<h1>Welcome to FastAPI Standard</h1>
				<p>
					FastAPI Standard is a compact full-stack starter that pairs a FastAPI API
					with a React and Vite frontend.
				</p>
				<p>
					It includes SQLite-backed authentication, bearer token
					sessions, typed routing, and a reusable component showcase without
					forcing login on public screens.
				</p>
			</section>
		</main>
	);
}
