<template>
  <div id="storageCard" class="card grow flex flex-col">
    <div class="card-header">
      <h3 class="text-header text-default">Pool Information</h3>
    </div>
    <div
      v-if="hasPoolInfo"
      class="card-body overflow-y-auto grow-0 flex flex-wrap gap-12"
    >
      <div
        class="grow-0 2xl:grow grid grid-cols-3 items-stretch gap-y-3 gap-x-5"
      >
        <div
          class="text-label text-default col-span-3 border-b-[1px] shrink-0 border-neutral-200 dark:border-neutral-700"
        >
          Pool
        </div>
        <div class="grid grid-cols-1">
          <div class="text-sm text-muted">name</div>
          <div class="text-sm break-words">{{ poolName }}</div>
        </div>
        <div class="grid grid-cols-1">
          <div class="text-sm text-muted">filesystem</div>
          <div class="text-sm break-words">{{ filesystem }}</div>
        </div>
        <div class="grid grid-cols-1">
          <div class="text-sm text-muted">status</div>
          <div class="text-sm break-words">{{ status }}</div>
        </div>
        <div class="grid grid-cols-1">
          <div class="text-sm text-muted">mountpoint</div>
          <div class="text-sm break-words">{{ mountpoint }}</div>
        </div>
        <div class="grid grid-cols-1">
          <div class="text-sm text-muted">members</div>
          <div class="text-sm break-words">{{ poolMembers.length }}</div>
        </div>
      </div>

      <div
        class="grow-0 2xl:grow grid grid-cols-3 items-stretch gap-y-3 gap-x-5"
      >
        <div
          class="text-label text-default col-span-3 border-b-[1px] shrink-0 border-neutral-200 dark:border-neutral-700"
        >
          Devices
        </div>
        <div>
          <div class="text-sm text-muted">slots</div>
          <div class="text-sm break-words">{{ slotSummary }}</div>
        </div>
        <div class="col-span-2">
          <div class="text-sm text-muted">devices</div>
          <div class="text-sm break-words">{{ deviceSummary }}</div>
        </div>
      </div>
    </div>
    <div v-else class="card-body grow flex justify-center items-center">
      <div class="p-5 bg-accent rounded-lg">
        <span class="text-muted">Click on a pool disk for more detail.</span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, inject } from "vue";

export default {
  setup() {
    const currentDisk = inject("currentDisk");
    const diskInfo = inject("diskInfo");

    const rows = computed(() => (diskInfo?.rows ? diskInfo.rows.flat() : []));
    const selectedDisk = computed(() =>
      rows.value.find((slot) => slot?.["bay-id"] === currentDisk.value)
    );
    const poolName = computed(() => selectedDisk.value?.["storage-label"] || "N/A");
    const hasPoolInfo = computed(
      () =>
        selectedDisk.value?.["storage-role"] === "pool" &&
        !!selectedDisk.value?.["storage-label"]
    );
    const poolMembers = computed(() => {
      if (!hasPoolInfo.value) return [];
      return rows.value.filter(
        (slot) =>
          slot?.["storage-role"] === "pool" &&
          slot?.["storage-label"] === selectedDisk.value["storage-label"]
      );
    });
    const firstValue = (key) => {
      const match = poolMembers.value.find((slot) => slot?.[key]);
      return match?.[key] || "N/A";
    };
    const uniqueValues = (key) =>
      Array.from(
        new Set(poolMembers.value.map((slot) => slot?.[key]).filter(Boolean))
      );
    const filesystem = computed(() => {
      const values = uniqueValues("fs-type");
      return values.length ? values.join(", ") : "N/A";
    });
    const status = computed(() => firstValue("fs-status"));
    const mountpoint = computed(() => firstValue("fs-mountpoint"));
    const slotSummary = computed(() => {
      const values = poolMembers.value.map((slot) => slot?.["bay-id"]).filter(Boolean);
      return values.length ? values.join(", ") : "N/A";
    });
    const deviceSummary = computed(() => {
      const values = poolMembers.value
        .map((slot) => slot?.dev || slot?.["dev-by-path"])
        .filter(Boolean);
      return values.length ? values.join(", ") : "N/A";
    });

    return {
      hasPoolInfo,
      poolName,
      poolMembers,
      filesystem,
      status,
      mountpoint,
      slotSummary,
      deviceSummary,
    };
  },
};
</script>
