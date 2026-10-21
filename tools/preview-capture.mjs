import { chromium } from 'playwright';
import { existsSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';

const VIEWPORT_PRESETS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 390, height: 844 }
];

async function captureViewportSnapshot(pageInstance, targetUrl, targetViewport, destinationDirectory) {
  await pageInstance.setViewportSize({
    width: targetViewport.width,
    height: targetViewport.height
  });
  await pageInstance.goto(targetUrl, { waitUntil: 'networkidle', timeout: 30000 });
  const snapshotFilename = `${targetViewport.name}.png`;
  const snapshotPath = resolve(destinationDirectory, snapshotFilename);
  await pageInstance.screenshot({ path: snapshotPath, fullPage: false });
  return snapshotPath;
}

export async function executeCaptureLoop(targetUrl = 'http://localhost:5173', targetDirectory = './previews') {
  if (!existsSync(targetDirectory)) {
    mkdirSync(targetDirectory, { recursive: true });
  }

  const browserInstance = await chromium.launch({ headless: true });
  const browserContext = await browserInstance.newContext();
  const pageInstance = await browserContext.newPage();
  const capturedFilePaths = [];

  try {
    for (const targetViewport of VIEWPORT_PRESETS) {
      const savedPath = await captureViewportSnapshot(
        pageInstance,
        targetUrl,
        targetViewport,
        targetDirectory
      );
      capturedFilePaths.push(savedPath);
    }
  } finally {
    await browserContext.close();
    await browserInstance.close();
  }

  return capturedFilePaths;
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(import.meta.filename)) {
  const inputUrl = process.argv[2] || 'http://localhost:5173';
  const outputDir = process.argv[3] || './previews';

  executeCaptureLoop(inputUrl, outputDir)
    .then((savedLocations) => {
      process.stdout.write(`Visual snapshots generated successfully:\n${savedLocations.join('\n')}\n`);
      process.exit(0);
    })
    .catch((executionError) => {
      process.stderr.write(`Capture failure: ${executionError.message}\n`);
      process.exit(1);
    });
}
