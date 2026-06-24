<!--
Copyright (C) 2022 Mark Hooper <mhooper@45drives.com>
                   Josh Boudreau <jboudreau@45drives.com>
This file is part of Cockpit File Sharing.
Cockpit File Sharing is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation, either version 3
of the License, or (at your option) any later version.
Cockpit File Sharing is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with Cockpit File Sharing.
If not, see <https://www.gnu.org/licenses/>. 
-->

<template>
	<div class="p-5 flex items-center bg-plugin-header font-redhat shadow-lg z-10">
		<div class="flex flex-row items-baseline basis-32 grow shrink-0">
			<img
				class="w-6 h-6 mr-0.5 self-center"
				:src="darkMode ? './assets/images/45d-fan-dark.svg' : './assets/images/45d-fan-light.svg'"
			/>
			<h1 class="text-2xl">
				<span
					class="text-red-800 dark:text-white font-bold font-source-sans-pro"
					:style="{ 'font-size': '1.6rem' }"
				>45</span>
				<span class="text-gray-800 dark:text-red-600">Drives</span>
			</h1>
		</div>
		<h1
			class="text-red-800 dark:text-white text-2xl grow-0 text-center"
		>{{ moduleName }}</h1>
		<div class="flex basis-32 justify-end grow shrink-0">
			<button
				@click="darkMode = !darkMode"
				id="theme-toggle"
				type="button"
				class="text-muted focus:outline-none"
			>
				<SunIcon v-if="darkMode" class="size-icon-lg" />
				<MoonIcon v-else class="size-icon-lg" />
			</button>
		</div>
	</div>
</template>

<script>
import "@fontsource/red-hat-text/700.css";
import "@fontsource/red-hat-text/400.css";
import "source-sans-pro/source-sans-pro.css";
import { SunIcon, MoonIcon } from "@heroicons/vue/solid";
import { ref, watch, inject } from "vue";

export default {
	props: {
		moduleName: String,
		darkModeInjectionKey: {type:Symbol,required:false,default:null}
	},
	setup(props) {
		const darkMode = props.darkModeInjectionKey ?? ref(true);
		// When embedded in the Unraid webGUI the plugin runs in a same-origin
		// iframe whose parent <html> carries Unraid's theme class
		// (Theme--black / Theme--gray => dark, Theme--white / Theme--azure =>
		// light). Detect it so the plugin matches Unraid's color mode.
		function detectUnraidDark() {
			try {
				const parentDoc = window.parent && window.parent.document;
				const parentHtml = parentDoc && parentDoc.documentElement;
				if (parentHtml && parentHtml !== document.documentElement) {
					const cls = parentHtml.className || "";
					if (/\bTheme--(black|gray|dark)\b/.test(cls)) return true;
					if (/\bTheme--(white|azure|light)\b/.test(cls)) return false;
				}
			} catch (e) {
				// Not embedded, or a cross-origin parent: fall back below.
			}
			return null;
		}
		function getTheme() {
			const unraidDark = detectUnraidDark();
			if (unraidDark !== null)
				return unraidDark;
			// Standalone / dev fallback: OS preference, then any saved choice.
			let prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
			let theme = localStorage.getItem("color-theme");
			if (theme === null)
				return prefersDark;
			if (theme === "dark")
				return true;
			return false;
		}
		darkMode.value = getTheme();
		if (darkMode.value) {
			document.documentElement.classList.add("dark");
		} else {
			document.documentElement.classList.remove("dark");
		}
		watch(() => darkMode.value, (darkMode, oldDarkMode) => {
			localStorage.setItem("color-theme", darkMode ? "dark" : "light");
			if (darkMode) {
				document.documentElement.classList.add("dark");
			} else {
				document.documentElement.classList.remove("dark");
			}
		}, { lazy: false });
		return {
			darkMode,
		};
	},
	components: {
		SunIcon,
		MoonIcon
	}
};
</script>