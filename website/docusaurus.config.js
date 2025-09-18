// Minimal Docusaurus config for Astonish project
module.exports = {
  title: 'Astonish',
  tagline: 'Zero-dependency generative art (flow-field & orbit-trap)',
  url: 'http://example.com',
  baseUrl: '/',
  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  organizationName: 'local',
  projectName: 'astonish',
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
