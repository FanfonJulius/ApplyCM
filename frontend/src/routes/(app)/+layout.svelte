<script lang="ts">
	import { page } from "$app/state";

	let { children } = $props();

	let mobileMenuOpen = $state(false);

	function toggleMobileMenu() {
		mobileMenuOpen = !mobileMenuOpen;
	}
	function closeMobileMenu() {
		mobileMenuOpen = false;
	}

	const navItems = [
		{ href: "/dashboard", label: "Dashboard" },
		{ href: "/discover", label: "Discover Schools" },
		{ href: "/career-guide", label: "AI Career Guide" },
		{ href: "/application/profile", label: "Application Profile", matchPrefix: "/application" },
		{ href: "/favorites", label: "Favorites" },
		{ href: "/settings", label: "Settings" }
	];

	function isActive(item: { href: string; matchPrefix?: string }): boolean {
		if (item.matchPrefix) {
			return page.url.pathname.startsWith(item.matchPrefix);
		}
		return page.url.pathname === item.href;
	}
</script>

<div class="app-layout">
	<!-- Mobile top bar: hamburger / logo / help -->
	<header class="mobile-topbar">
		<button class="icon-button" onclick={toggleMobileMenu} aria-label="Open menu" aria-expanded={mobileMenuOpen}>
			<svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden="true">
				<path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
			</svg>
			<span>Menu</span>
		</button>

		<a class="logo" href="/dashboard">
			<svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
				<path d="M4 20 L12 4 L20 20 Z" fill="none" stroke="#2563eb" stroke-width="2" />
			</svg>
			<span>ApplyCM</span>
		</a>

		<button class="icon-button" aria-label="Help">
			<svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden="true">
				<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2" />
				<path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .8-1 1.5v.4" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
				<circle cx="12" cy="16.5" r="0.75" fill="currentColor" />
			</svg>
			<span>Help</span>
		</button>
	</header>

	{#if mobileMenuOpen}
		<button class="backdrop" onclick={closeMobileMenu} aria-label="Close menu"></button>
	{/if}

	<nav class="sidebar" class:open={mobileMenuOpen}>
		<a class="logo desktop-logo" href="/dashboard">
			<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true">
				<path d="M4 20 L12 4 L20 20 Z" fill="none" stroke="#2563eb" stroke-width="2.5" />
			</svg>
			<span>ApplyCM</span>
		</a>

		<ul>
			{#each navItems as item}
				{@const active = isActive(item)}
				<li>
					<a
						href={item.href}
						class:active
						onclick={closeMobileMenu}
					>
						{item.label}
					</a>
				</li>
			{/each}
		</ul>
	</nav>

	<main class="content">
		{@render children()}
	</main>
</div>

<style>
	:global(body) {
		margin: 0;
	}

	.app-layout {
		display: flex;
		min-height: 100vh;
		background: #f7fafc;
	}

	.mobile-topbar {
		display: none;
	}

	.sidebar {
		width: 250px;
		flex-shrink: 0;
		background-color: #1a202c;
		color: white;
		padding: 2rem 1rem;
	}
	.logo {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 1.5rem;
		font-weight: bold;
		margin-bottom: 2rem;
		text-decoration: none;
		color: inherit;
	}
	.sidebar ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}
	.sidebar ul li {
		margin-bottom: 0.5rem;
	}
	.sidebar ul li a {
		color: #a0aec0;
		text-decoration: none;
		display: block;
		padding: 0.75rem 1rem;
		border-radius: 8px;
		font-size: 0.95rem;
		font-weight: 500;
		transition: all 0.2s ease;
		border-left: 4px solid transparent;
	}
	.sidebar ul li a:hover {
		background-color: #2d3748;
		color: white;
	}
	/* Active Tab Highlight: Blue background, accent blue border, bold text */
	.sidebar ul li a.active {
		background-color: #2563eb;
		color: #ffffff;
		font-weight: 600;
		border-left: 4px solid #93c5fd;
		box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
	}

	.backdrop {
		display: none;
	}

	.content {
		flex: 1;
		padding: 2rem;
		background-color: #f7fafc;
		min-width: 0;
	}

	@media (max-width: 768px) {
		.app-layout {
			flex-direction: column;
		}

		.mobile-topbar {
			display: flex;
			align-items: center;
			justify-content: space-between;
			background: #fff;
			border-bottom: 1px solid #e2e8f0;
			padding: 0.75rem 1rem;
			position: sticky;
			top: 0;
			z-index: 20;
		}
		.mobile-topbar .logo {
			margin: 0;
			font-size: 1.1rem;
			color: #1a2b4a;
		}
		.icon-button {
			display: flex;
			align-items: center;
			gap: 0.35rem;
			background: none;
			border: none;
			color: #1a2b4a;
			font-size: 0.9rem;
			cursor: pointer;
			padding: 0.25rem;
		}

		.sidebar {
			position: fixed;
			top: 0;
			left: 0;
			height: 100vh;
			transform: translateX(-100%);
			transition: transform 0.2s ease;
			z-index: 30;
			overflow-y: auto;
		}
		.sidebar.open {
			transform: translateX(0);
		}
		.desktop-logo {
			display: none;
		}

		.backdrop {
			display: block;
			position: fixed;
			inset: 0;
			background: rgba(0, 0, 0, 0.4);
			border: none;
			z-index: 25;
			padding: 0;
		}

		.content {
			padding: 1rem;
		}
	}
</style>