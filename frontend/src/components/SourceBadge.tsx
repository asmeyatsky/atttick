"use client";

import styles from "@/styles/chat.module.css";

interface SourceBadgeProps {
  sources: string[];
  isVerified: boolean;
}

export function SourceBadge({ sources, isVerified }: SourceBadgeProps) {
  if (!isVerified && sources.length === 0) return null;

  return (
    <span className={styles.sourceBadge}>
      <span className={styles.sourceBadgeIcon}>&#10003;</span>
      Verified by Staff History
      {sources.length > 1 && (
        <span className={styles.sourceCount}>({sources.length} sources)</span>
      )}
    </span>
  );
}
