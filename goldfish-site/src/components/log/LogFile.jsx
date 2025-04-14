import { useState } from 'react';
import styles from './LogFile.module.css';

export default function LogFile({ filename, size, children, defaultOpen = false }) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={styles.entry}>
      <button className={styles.fileRow} onClick={() => setOpen(o => !o)}>
        <span className={styles.connector}>{open ? '`--' : '|--'}</span>
        <span className={styles.size}>[ {size} ]</span>
        <span className={styles.filename}>{filename}</span>
      </button>
      {open && (
        <div className={styles.content}>
          {children}
        </div>
      )}
    </div>
  );
}
