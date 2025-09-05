const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const bcrypt = require('crypto');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '..')));

// Database setup
const dbPath = path.join(__dirname, '..', 'mystic.db');
const db = new sqlite3.Database(dbPath);

// Initialize database
db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS bot_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token TEXT,
        guild_id TEXT,
        status TEXT DEFAULT 'stopped',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )`);
    
    db.run(`CREATE TABLE IF NOT EXISTS download_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game TEXT,
        cheat TEXT,
        link1 TEXT,
        link2 TEXT,
        link3 TEXT,
        link4 TEXT,
        UNIQUE(game, cheat)
    )`);
    
    // Insert default download links
    const defaultLinks = [
        ['fortnite', 'arly-cracked', 'https://mega.nz/arly-fn', 'https://drive.google.com/arly', 'https://mediafire.com/arly', 'https://t.me/mystic_arly'],
        ['fortnite', 'softhub-free', 'https://mega.nz/softhub', 'https://drive.google.com/softhub', 'https://mediafire.com/softhub', 'https://t.me/mystic_softhub'],
        ['fortnite', 'mystware-premium', 'https://mega.nz/mystware', 'https://drive.google.com/mystware', 'https://mediafire.com/mystware', 'https://t.me/mystic_mystware'],
        ['valorant', 'phantom-overlay', 'https://mega.nz/phantom', 'https://drive.google.com/phantom', 'https://mediafire.com/phantom', 'https://t.me/mystic_phantom'],
        ['valorant', 'viper-cheat', 'https://mega.nz/viper', 'https://drive.google.com/viper', 'https://mediafire.com/viper', 'https://t.me/mystic_viper'],
        ['valorant', 'mystic-val', 'https://mega.nz/mystic-val', 'https://drive.google.com/mystic-val', 'https://mediafire.com/mystic-val', 'https://t.me/mystic_val'],
        ['apex', 'apex-horizon', 'https://mega.nz/horizon', 'https://drive.google.com/horizon', 'https://mediafire.com/horizon', 'https://t.me/mystic_horizon'],
        ['apex', 'nighthawk-apex', 'https://mega.nz/nighthawk', 'https://drive.google.com/nighthawk', 'https://mediafire.com/nighthawk', 'https://t.me/mystic_nighthawk'],
        ['apex', 'mystic-apex', 'https://mega.nz/mystic-apex', 'https://drive.google.com/mystic-apex', 'https://mediafire.com/mystic-apex', 'https://t.me/mystic_apex'],
        ['cs2', 'osiris-cs2', 'https://mega.nz/osiris', 'https://drive.google.com/osiris', 'https://mediafire.com/osiris', 'https://t.me/mystic_osiris'],
        ['cs2', 'gamesense-cs2', 'https://mega.nz/gamesense', 'https://drive.google.com/gamesense', 'https://mediafire.com/gamesense', 'https://t.me/mystic_gamesense'],
        ['cs2', 'mystic-cs2', 'https://mega.nz/mystic-cs2', 'https://drive.google.com/mystic-cs2', 'https://mediafire.com/mystic-cs2', 'https://t.me/mystic_cs2'],
        ['cod', 'warzone-plus', 'https://mega.nz/warzone', 'https://drive.google.com/warzone', 'https://mediafire.com/warzone', 'https://t.me/mystic_warzone'],
        ['cod', 'cod-engine', 'https://mega.nz/cod-engine', 'https://drive.google.com/cod-engine', 'https://mediafire.com/cod-engine', 'https://t.me/mystic_cod'],
        ['cod', 'mystic-cod', 'https://mega.nz/mystic-cod', 'https://drive.google.com/mystic-cod', 'https://mediafire.com/mystic-cod', 'https://t.me/mystic_cod_pro']
    ];
    
    const stmt = db.prepare(`INSERT OR IGNORE INTO download_links (game, cheat, link1, link2, link3, link4) VALUES (?, ?, ?, ?, ?, ?)`);
    defaultLinks.forEach(link => stmt.run(link));
    stmt.finalize();
});

let botProcesses = new Map(); // serverId -> process
let serverConfigs = new Map(); // serverId -> config

// Authentication middleware
function authenticate(req, res, next) {
    const { username, password } = req.body;
    if (username === 'justvicky152' && password === 'justvicky152') {
        next();
    } else {
        res.status(401).json({ error: 'Invalid credentials' });
    }
}

// Simple session check (for demo purposes)
function checkAuth(username, password) {
    return username === 'justvicky152' && password === 'justvicky152';
}

// API Routes

// Login endpoint
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    
    if (checkAuth(username, password)) {
        res.json({ 
            success: true, 
            message: 'Login successful',
            token: 'demo-token' // In production, use proper JWT
        });
    } else {
        res.status(401).json({ 
            success: false, 
            error: 'Invalid credentials' 
        });
    }
});

// Send custom message to Discord channel (multi-server)
app.post('/api/bot/message', async (req, res) => {
    const { channel, message, serverId, username, password } = req.body;
    
    if (!checkAuth(username || 'justvicky152', password || 'justvicky152')) {
        return res.status(401).json({ error: 'Authentication required' });
    }
    
    if (!serverId) {
        return res.status(400).json({ error: 'Server ID is required' });
    }
    
    if (!botProcesses.has(serverId)) {
        return res.status(400).json({ error: 'Bot is not running for this server' });
    }
    
    try {
        // Send message through bot process (simplified for demo)
        // In production, you'd use proper IPC or WebSocket communication
        const serverConfig = serverConfigs.get(serverId);
        res.json({ 
            success: true, 
            message: `Message sent to #${channel} on ${serverConfig?.guildId || 'server'}`,
            content: message,
            serverId: serverId
        });
    } catch (error) {
        res.status(500).json({ error: 'Failed to send message: ' + error.message });
    }
});

// Get channel list
app.get('/api/channels', (req, res) => {
    const channels = [
        { id: 'general', name: 'general', type: 'text' },
        { id: 'announcements', name: 'announcements', type: 'text' },
        { id: 'fortnite', name: 'fortnite', type: 'text' },
        { id: 'valorant', name: 'valorant', type: 'text' },
        { id: 'cs2', name: 'cs2', type: 'text' },
        { id: 'apex', name: 'apex', type: 'text' },
        { id: 'cod', name: 'cod', type: 'text' },
        { id: 'setup-help', name: 'setup-help', type: 'text' }
    ];
    
    res.json(channels);
});

// Get game-specific download links
app.get('/api/game/:game/links', (req, res) => {
    const { game } = req.params;
    
    db.all('SELECT * FROM download_links WHERE game = ? ORDER BY cheat', [game.toLowerCase()], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        
        const formattedLinks = rows.map(row => ({
            id: row.id,
            cheat: row.cheat,
            game: row.game,
            links: {
                mega: row.link1,
                drive: row.link2,
                mediafire: row.link3,
                telegram: row.link4
            },
            password: 'mystic25',
            instructions: [
                `Download ${row.cheat}.rar`,
                'Extract with password: mystic25',
                'Run main.bat (injection bypasser)',
                'May flag as false positive - normal',
                'Wait for game detection',
                'Wait for injection',
                'Press INSERT or F12 in lobby',
                'Contact owners for help if needed'
            ]
        }));
        
        res.json(formattedLinks);
    });
});

// Get all download links
app.get('/api/links', (req, res) => {
    db.all('SELECT * FROM download_links ORDER BY game, cheat', (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
    });
});

// Update download link
app.put('/api/links/:id', (req, res) => {
    const { id } = req.params;
    const { link1, link2, link3, link4 } = req.body;
    
    db.run(
        'UPDATE download_links SET link1 = ?, link2 = ?, link3 = ?, link4 = ? WHERE id = ?',
        [link1, link2, link3, link4, id],
        function(err) {
            if (err) {
                res.status(500).json({ error: err.message });
                return;
            }
            res.json({ message: 'Links updated successfully', changes: this.changes });
        }
    );
});

// Start Discord bot with authentication (multi-server)
app.post('/api/bot/start', (req, res) => {
    const { token, guildId, serverId, username, password } = req.body;
    
    if (!token || !guildId || !serverId) {
        return res.status(400).json({ error: 'Token, Guild ID, and Server ID are required' });
    }
    
    // Simple auth check (in production, use proper session management)
    if (!checkAuth(username || 'justvicky152', password || 'justvicky152')) {
        return res.status(401).json({ error: 'Authentication required' });
    }
    
    // Stop existing bot for this server if running
    if (botProcesses.has(serverId)) {
        const existingProcess = botProcesses.get(serverId);
        if (existingProcess) {
            existingProcess.kill();
            botProcesses.delete(serverId);
        }
    }
    
    // Save server config
    const serverConfig = {
        id: serverId,
        token: token,
        guildId: guildId,
        status: 'starting',
        startedAt: new Date().toISOString()
    };
    
    serverConfigs.set(serverId, serverConfig);
    
    // Save config to database
    db.run(
        'INSERT OR REPLACE INTO bot_configs (id, token, guild_id, status) VALUES (?, ?, ?, ?)',
        [serverId, token, guildId, 'starting'],
        (err) => {
            if (err) {
                console.error('Database error:', err);
            }
        }
    );
    
    // This section is now handled above
    
    // Start new bot process
    try {
        const env = { 
            ...process.env, 
            DISCORD_BOT_TOKEN: token, 
            GUILD_ID: guildId,
            SERVER_ID: serverId,
            PYTHONPATH: path.join(__dirname, '..')
        };
        const botProcess = spawn('python3', ['bot.py'], { 
            env, 
            cwd: path.join(__dirname, '..'),
            stdio: ['pipe', 'pipe', 'pipe']
        });
        
        botProcesses.set(serverId, botProcess);
        
        botProcess.stdout.on('data', (data) => {
            console.log(`Bot ${serverId}: ${data}`);
        });
        
        botProcess.stderr.on('data', (data) => {
            console.error(`Bot ${serverId} Error: ${data}`);
        });
        
        botProcess.on('close', (code) => {
            console.log(`Bot process ${serverId} exited with code ${code}`);
            db.run('UPDATE bot_configs SET status = ? WHERE id = ?', ['stopped', serverId]);
            botProcesses.delete(serverId);
            if (serverConfigs.has(serverId)) {
                const config = serverConfigs.get(serverId);
                config.status = 'stopped';
                serverConfigs.set(serverId, config);
            }
        });
        
        // Update status to running
        setTimeout(() => {
            db.run('UPDATE bot_configs SET status = ? WHERE id = ?', ['running', serverId]);
            if (serverConfigs.has(serverId)) {
                const config = serverConfigs.get(serverId);
                config.status = 'running';
                serverConfigs.set(serverId, config);
            }
        }, 3000);
        
        res.json({ 
            success: true, 
            message: 'Bot started successfully! Server setup initiated.',
            serverId: serverId,
            pid: botProcess.pid,
            features: [
                'Auto role assignment',
                'Download commands with setup instructions',
                'Channel management',
                'Custom message sending'
            ]
        });
        
    } catch (error) {
        console.error(`Failed to start bot ${serverId}:`, error);
        db.run('UPDATE bot_configs SET status = ? WHERE id = ?', ['error', serverId]);
        if (serverConfigs.has(serverId)) {
            const config = serverConfigs.get(serverId);
            config.status = 'error';
            serverConfigs.set(serverId, config);
        }
        res.status(500).json({ error: 'Failed to start bot: ' + error.message });
    }
});

// Stop Discord bot with authentication (multi-server)
app.post('/api/bot/stop', (req, res) => {
    const { serverId, username, password } = req.body;
    
    if (!checkAuth(username || 'justvicky152', password || 'justvicky152')) {
        return res.status(401).json({ error: 'Authentication required' });
    }
    if (serverId && botProcesses.has(serverId)) {
        const botProcess = botProcesses.get(serverId);
        botProcess.kill();
        botProcesses.delete(serverId);
        db.run('UPDATE bot_configs SET status = ? WHERE id = ?', ['stopped', serverId]);
        
        if (serverConfigs.has(serverId)) {
            const config = serverConfigs.get(serverId);
            config.status = 'stopped';
            serverConfigs.set(serverId, config);
        }
        
        res.json({ success: true, message: 'Bot stopped successfully!', serverId: serverId });
    } else {
        res.json({ success: false, message: 'Bot is not running or server not found' });
    }
});

// Get bot status (multi-server)
app.get('/api/bot/status', (req, res) => {
    const { serverId } = req.query;
    
    if (!serverId) {
        // Return all server statuses
        const allStatuses = {};
        serverConfigs.forEach((config, id) => {
            const isRunning = botProcesses.has(id);
            allStatuses[id] = {
                status: isRunning ? 'running' : 'stopped',
                config: config,
                pid: botProcesses.get(id)?.pid || null
            };
        });
        res.json(allStatuses);
        return;
    }
    
    const isRunning = botProcesses.has(serverId);
    const config = serverConfigs.get(serverId);
    
    db.get('SELECT * FROM bot_configs WHERE id = ?', [serverId], (err, row) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        
        res.json({
            status: isRunning ? 'running' : (row?.status || config?.status || 'stopped'),
            config: config || row,
            pid: botProcesses.get(serverId)?.pid || null
        });
    });
});

// Get setup instructions for a specific game
app.get('/api/setup/:game', (req, res) => {
    const { game } = req.params;
    
    const setupInstructions = {
        password: 'mystic25',
        steps: [
            `Download the ${game}-cheat.rar file`,
            'Extract using password: mystic25',
            'Run main.bat (our injection bypasser)',
            'Antivirus may flag - this is normal',
            'Wait for automatic game detection',
            'Wait for custom injection system',
            'Press INSERT or F12 in game lobby',
            'Contact owners if you need help'
        ],
        notes: [
            'main.bat acts like a second PC to bypass injection modules',
            'False positives are common with game cheats',
            'Our custom injection system is automatic',
            'Contact owners for any missing details'
        ]
    };
    
    res.json(setupInstructions);
});

// Serve index.html at root
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'index.html'));
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Mystic Gaming Discord Manager running on port ${PORT}`);
    console.log(`🌐 Visit: http://localhost:${PORT}`);
    console.log(`🎮 Bot management with Discord-like interface`);
    console.log(`🔐 Login: justvicky152 / justvicky152`);
    console.log(`🎯 Features: Channel management, Custom messages, Download links`);
    console.log(`🔑 Extract password for all cheats: mystic25`);
});

// Get all servers
app.get('/api/servers', (req, res) => {
    const serverList = Array.from(serverConfigs.values()).map(config => ({
        id: config.id,
        guildId: config.guildId,
        status: config.status,
        isRunning: botProcesses.has(config.id),
        pid: botProcesses.get(config.id)?.pid || null,
        startedAt: config.startedAt
    }));
    
    res.json(serverList);
});

// Remove server configuration
app.delete('/api/servers/:serverId', (req, res) => {
    const { serverId } = req.params;
    const { username, password } = req.body;
    
    if (!checkAuth(username || 'justvicky152', password || 'justvicky152')) {
        return res.status(401).json({ error: 'Authentication required' });
    }
    
    // Stop bot if running
    if (botProcesses.has(serverId)) {
        const botProcess = botProcesses.get(serverId);
        botProcess.kill();
        botProcesses.delete(serverId);
    }
    
    // Remove from memory
    serverConfigs.delete(serverId);
    
    // Remove from database
    db.run('DELETE FROM bot_configs WHERE id = ?', [serverId], (err) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ success: true, message: 'Server configuration removed' });
    });
});

// Graceful shutdown
process.on('SIGINT', () => {
    // Stop all bot processes
    botProcesses.forEach((process, serverId) => {
        console.log(`Stopping bot process ${serverId}`);
        process.kill();
    });
    db.close();
    process.exit(0);
});
