import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync } from 'fs';
import os from 'os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());

// Load configuration
let config;
try {
  const configPath = join(__dirname, '..', 'config.json');
  const configData = readFileSync(configPath, 'utf-8');
  config = JSON.parse(configData);
} catch (error) {
  console.error('Error loading config.json:', error.message);
  process.exit(1);
}

app.post('/render', async (req, res) => {
  const { postCount, color } = req.body;

  // Validate input
  if (!postCount || !['4', '6'].includes(postCount)) {
    return res.status(400).json({ error: 'Invalid postCount. Must be "4" or "6"' });
  }

  if (!color || !['red', 'blue', 'white'].includes(color)) {
    return res.status(400).json({ error: 'Invalid color. Must be "red", "blue", or "white"' });
  }

  try {
    // Get Blender executable path (default to 'blender' command, can be overridden in config)
    const blenderPath = config.blenderPath || 'blender';
    
    // Path to the Python script
    const scriptPath = join(__dirname, 'scripts', 'blender_render.py');
    
    // Get desktop path
    const desktopPath = join(os.homedir(), 'Desktop');
    
    // Generate output filename
    const timestamp = Date.now();
    const outputPath = join(desktopPath, `blender_render_${postCount}post_${color}_${timestamp}.png`);

    // Prepare arguments for Blender
    const args = [
      '--background',
      '--python',
      scriptPath,
      '--',
      `--base-file=${config.baseFile}`,
      `--component-file=${config.componentFile}`,
      `--post-count=${postCount}`,
      `--color=${color}`,
      `--output=${outputPath}`,
      `--spacing=${config.spacing || 2}`,
    ];

    console.log(`Starting Blender render: ${blenderPath} ${args.join(' ')}`);

    // Spawn Blender process
    const blenderProcess = spawn(blenderPath, args, {
      cwd: __dirname,
      stdio: 'pipe',
    });

    let stdout = '';
    let stderr = '';

    blenderProcess.stdout.on('data', (data) => {
      stdout += data.toString();
      console.log(`Blender stdout: ${data.toString()}`);
    });

    blenderProcess.stderr.on('data', (data) => {
      stderr += data.toString();
      console.error(`Blender stderr: ${data.toString()}`);
    });

    blenderProcess.on('close', (code) => {
      if (code === 0) {
        res.json({
          success: true,
          outputPath: outputPath,
          message: 'Render completed successfully',
        });
      } else {
        res.status(500).json({
          error: 'Blender render failed',
          details: stderr || stdout,
          exitCode: code,
        });
      }
    });

    blenderProcess.on('error', (error) => {
      res.status(500).json({
        error: 'Failed to start Blender process',
        details: error.message,
      });
    });

  } catch (error) {
    res.status(500).json({
      error: 'Internal server error',
      details: error.message,
    });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});

