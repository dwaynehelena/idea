import React from 'react';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';

export default function Home() {
  return (
    <div style={{padding: 20}}>
      <h1>Astonish</h1>
      <p>Zero-dependency generative art in a single Python file.</p>
      <p>
        <Link to={useBaseUrl('docs/intro')}>Read the docs</Link>
      </p>
      <p>
        Sample outputs live in <code>outputs/</code> — open them locally to view the full-resolution images.
      </p>
    </div>
  );
}
