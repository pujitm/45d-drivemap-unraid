// Vendored subset of @45drives/cockpit-helpers.
//
// The upstream package is published only to 45Drives' private GitHub Packages
// registry, which makes the project impossible to build without registry
// credentials. This app only uses the five helpers below, all of which depend
// solely on Vue reactivity and the global `cockpit` object, so we vendor them
// here and drop the private dependency. Implementations mirror the published
// package (extracted from the compiled bundle).

import { reactive, watch } from "vue";

export function errorString(state) {
  if (typeof state === "string") return state;
  return state?.stderr ?? state?.message ?? JSON.stringify(state);
}

export function errorStringHTML(state) {
  if (typeof state === "string")
    return `<span class="text-gray-500 font-mono text-sm whitespace-pre-wrap">${state}</span>`;
  return (
    state.errorStringHTML?.call(state) ??
    `<span class="text-gray-500 font-mono text-sm whitespace-pre-wrap">${state?.stderr ?? state?.message ?? JSON.stringify(state)}</span>`
  );
}

export function useSpawn(argv = [], opts = {}, stderr = "message") {
  const state = reactive({
    loading: true,
    status: 0,
    stdout: "",
    stderr: "",
    argv: [],
    proc: null,
    promise() {
      return new Promise((resolve, reject) => {
        watch(
          state,
          () => {
            if (!state.loading) {
              if (state.status === 0) resolve({ ...state });
              else reject({ ...state });
            }
          },
          { lazy: false, immediate: true }
        );
      });
    },
    argvPretty() {
      return argv.map((token) => (/\s/.test(token) ? `"${token}"` : token)).join(" ");
    },
    errorStringHTML(fullArgv = false) {
      return (
        `<span class="font-mono text-sm whitespace-pre-wrap"><span class="font-semibold">${this.argv[0]}: </span><span>${errorString(this)} </span>` +
        (fullArgv ? `<span class="text-gray-500 font-mono text-sm">${this.argvPretty()}</span>` : "") +
        "</span>"
      );
    },
  });

  if (!opts.superuser) opts.superuser = "require";
  if (!opts.err) opts.err = stderr;

  state.loading = true;
  state.status = 0;
  state.stdout = "";
  state.stderr = "";
  state.argv = [...argv];
  state.proc = cockpit.spawn(argv, opts);
  state.proc
    .then((_stdout, _stderr) => {
      state.stdout = _stdout;
      state.stderr = _stderr;
    })
    .catch((ex, _stdout) => {
      state.stdout = _stdout;
      state.stderr = ex.message ?? ex.problem;
      state.status = ex.exit_status;
    })
    .finally(() => {
      state.loading = false;
    });

  return state;
}

export class FIFO {
  constructor() {
    this.arr = [];
    this.len = 0;
  }
  push(obj) {
    this.len++;
    this.arr.push(obj);
  }
  pop() {
    const obj = this.arr.shift() ?? null;
    if (obj) this.len--;
    return obj;
  }
  getLen() {
    return this.len;
  }
}

export class UniqueIDGenerator {
  constructor(maxIds = Number.MAX_SAFE_INTEGER) {
    this.id = 0;
    this.maxIds = maxIds;
    this.reuptake = [];
  }
  get() {
    if (this.id == this.maxIds && this.reuptake.length === 0)
      throw new Error("Unique ID limit reached");
    return this.reuptake.length ? this.reuptake.shift() : this.id++;
  }
  release(id) {
    if (this.reuptake.includes(id)) throw new Error("Double release of unique ID");
    if (id >= this.id) throw new Error("Released ID was never given");
    this.reuptake.push(id);
  }
}
