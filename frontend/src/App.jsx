import React, { useState, useEffect, useRef } from 'react'
import { Routes, Route, Link, useLocation } from 'react-router-dom'
import {
  Zap, Users, MessageSquare, Cpu, Activity, Settings,
  Play, Pause, RotateCcw, Plus, Trash2, ChevronRight,
  Terminal, Brain, Code, Sparkles, Shield, GitBranch,
  Server, Database, Box, BarChart3, Clock, CheckCircle,
  AlertTriangle, XCircle, Loader2, Send, Bot, User,
  FileCode, Layers, Workflow, TrendingUp, Eye, Lock,
  Globe, Wifi, WifiOff, Copy, Download, Upload, Search,
  Filter, SortAsc, Grid, List, Moon, Sun, Menu, X,
  ChevronDown, ExternalLink, Bookmark, Heart, Share2,
  MoreHorizontal, Bell, Mail, Calendar, Folder, FileText,
  Image, Music, Video, MapPin, Phone, Video as VideoIcon,
  Mic, Camera, Printer, Save, Edit, Trash, Undo, Redo,
  Maximize, Minimize, RefreshCw, LogIn, LogOut, UserPlus,
  Key, ShieldCheck, Fingerprint, Scan, QrCode, Barcode,
  CreditCard, DollarSign, ShoppingCart, Package, Truck,
  Home, Building, Landmark, Factory, Warehouse, Store,
  Hotel, Hospital, School, Church, Castle, TreePine,
  Mountain, Sun as SunIcon, Cloud, CloudRain, CloudSnow,
  Wind, Thermometer, Droplets, Flame, Snowflake, Rainbow,
  Umbrella, Sunglasses, Anchor, Ship, Plane, Train, Bus,
  Car, Bike, Footprints, Map, Compass, Navigation, Target,
  Crosshair, Swords, Crown, Trophy,
  Medal, Award, Star, ThumbsUp, ThumbsDown, Smile, Frown,
  Meh, Laugh, Angry, Heart as HeartIcon, HeartCrack, Flower2,
  Leaf, TreeDeciduous, Sprout, Recycle, Battery, BatteryCharging,
  BatteryFull, BatteryMedium, BatteryLow, BatteryWarning, Plug,
  Lightbulb, Flashlight, Lamp, Candle, FlameKindling, FireExtinguisher,
  Hammer, Wrench, Screwdriver, Drill, Saw, Axe, Pickaxe, Shovel,
  Ruler, PenTool, Paintbrush, Palette, Eraser, Scissors, Sticker,
  StickyNote, Clipboard, ClipboardList, ClipboardCheck, BookOpen,
  Book, BookMarked, Library, GraduationCap, Glasses, Microscope,
  Telescope, FlaskConical, Atom, Dna, Pill, Syringe, Stethoscope,
  HeartPulse, Activity as ActivityIcon, Brain as BrainIcon, Eye as EyeIcon,
  Ear, Bone, Footprints as FootprintsIcon, Hand, Fist, Pointer,
  Mouse, Keyboard, Monitor, Laptop, Tablet, Smartphone, Watch,
  Headphones, Speaker, Radio, Tv, Projector, Gamepad2, Dice5,
  Puzzle, ToyBrick, Blocks, Shapes, Circle, Square, Triangle,
  Hexagon, Octagon, Star as StarIcon, Diamond, Crown as CrownIcon,
  Gem, Coins, Banknote, Wallet, PiggyBank, Receipt, Invoice,
  FileSpreadsheet, FileBarChart, FilePieChart, FileLineChart,
  Presentation, Slideshow, Type, Heading, Text, AlignLeft,
  AlignCenter, AlignRight, AlignJustify, Bold, Italic, Underline,
  Strikethrough, Code as CodeIcon, Quote, List as ListIcon,
  ListOrdered, ListChecks, Indent, Outdent, Link as LinkIcon,
  Link2, Unlink, Paperclip, Pin, PinOff, Bookmark as BookmarkIcon,
  BookmarkPlus, Tag, Tags, Hash, At, Mention, Reply, ReplyAll,
  Forward, Send as SendIcon, Mail as MailIcon, Inbox, Archive,
  Trash as TrashIcon, Delete, Eraser as EraserIcon, Scissors as ScissorsIcon,
  Copy as CopyIcon, Clipboard as ClipboardIcon, ClipboardCopy,
  ClipboardPaste, ClipboardX, File as FileIcon, FilePlus,
  FileMinus, FileX, FileCheck, FileClock, FileCode as FileCodeIcon,
  FileJson, FileType, FileImage, FileVideo, FileAudio, FileArchive,
  FileUp, FileDown, Folder as FolderIcon, FolderPlus, FolderMinus,
  FolderOpen, FolderTree, FolderCheck, FolderX, FolderClock,
  FolderCode, FolderGit, FolderGit2, FolderKanban, FolderCog,
  FolderLock, FolderHeart, FolderSearch, FolderSync, Folders,
  HardDrive, Database as DatabaseIcon, Server as ServerIcon,
  Cloud as CloudIcon, CloudUpload, CloudDownload, CloudRain as CloudRainIcon,
  CloudSnow as CloudSnowIcon, CloudLightning, CloudFog, CloudSun,
  CloudMoon, CloudDrizzle, Haze, ThermometerSun, ThermometerSnowflake,
  Droplets as DropletsIcon, Droplet, Water, Waves, Umbrella as UmbrellaIcon,
  Snowflake as SnowflakeIcon, Wind as WindIcon, Tornado, Hurricane,
  Earthquake, Volcano, Mountain as MountainIcon, MountainSnow,
  TreePine as TreePineIcon, TreeDeciduous as TreeDeciduousIcon,
  Flower2 as Flower2Icon, Leaf as LeafIcon, Sprout as SproutIcon,
  Recycle as RecycleIcon, Trash2 as Trash2Icon, RecycleIcon,
  Battery as BatteryIcon, BatteryCharging as BatteryChargingIcon,
  BatteryFull as BatteryFullIcon, BatteryMedium as BatteryMediumIcon,
  BatteryLow as BatteryLowIcon, BatteryWarning as BatteryWarningIcon,
  Plug as PlugIcon, Zap as ZapIcon, Lightbulb as LightbulbIcon,
  Flashlight as FlashlightIcon, Lamp as LampIcon, Candle as CandleIcon,
  FlameKindling as FlameKindlingIcon, FireExtinguisher as FireExtinguisherIcon,
  Hammer as HammerIcon, Wrench as WrenchIcon, Screwdriver as ScrewdriverIcon,
  Drill as DrillIcon, Saw as SawIcon, Axe as AxeIcon, Pickaxe as PickaxeIcon,
  Shovel as ShovelIcon, Ruler as RulerIcon, PenTool as PenToolIcon,
  Paintbrush as PaintbrushIcon, Palette as PaletteIcon, Eraser as EraserIcon2,
  Scissors as ScissorsIcon2, Sticker as StickerIcon, StickyNote as StickyNoteIcon,
  Clipboard as ClipboardIcon2, ClipboardList as ClipboardListIcon,
  ClipboardCheck as ClipboardCheckIcon, BookOpen as BookOpenIcon,
  Book as BookIcon, BookMarked as BookMarkedIcon, Library as LibraryIcon,
  GraduationCap as GraduationCapIcon, Glasses as GlassesIcon,
  Microscope as MicroscopeIcon, Telescope as TelescopeIcon,
  FlaskConical as FlaskConicalIcon, Atom as AtomIcon, Dna as DnaIcon,
  Pill as PillIcon, Syringe as SyringeIcon, Stethoscope as StethoscopeIcon,
  HeartPulse as HeartPulseIcon, ActivityIcon, BrainIcon, EyeIcon,
  Ear as EarIcon, Bone as BoneIcon, FootprintsIcon, Hand as HandIcon,
  Fist as FistIcon, Pointer as PointerIcon, Mouse as MouseIcon,
  Keyboard as KeyboardIcon, Monitor as MonitorIcon, Laptop as LaptopIcon,
  Tablet as TabletIcon, Smartphone as SmartphoneIcon, Watch as WatchIcon,
  Headphones as HeadphonesIcon, Speaker as SpeakerIcon, Radio as RadioIcon,
  Tv as TvIcon, Projector as ProjectorIcon, Gamepad2 as Gamepad2Icon,
  Dice5 as Dice5Icon, Puzzle as PuzzleIcon, ToyBrick as ToyBrickIcon,
  Blocks as BlocksIcon, Shapes as ShapesIcon, Circle as CircleIcon,
  Square as SquareIcon, Triangle as TriangleIcon, Hexagon as HexagonIcon,
  Octagon as OctagonIcon, StarIcon, Diamond as DiamondIcon,
  CrownIcon, Gem as GemIcon, Coins as CoinsIcon, Banknote as BanknoteIcon,
  Wallet as WalletIcon, PiggyBank as PiggyBankIcon, Receipt as ReceiptIcon,
  Invoice as InvoiceIcon, FileSpreadsheet as FileSpreadsheetIcon,
  FileBarChart as FileBarChartIcon, FilePieChart as FilePieChartIcon,
  FileLineChart as FileLineChartIcon, Presentation as PresentationIcon,
  Slideshow as SlideshowIcon, Type as TypeIcon, Heading as HeadingIcon,
  Text as TextIcon, AlignLeft as AlignLeftIcon, AlignCenter as AlignCenterIcon,
  AlignRight as AlignRightIcon, AlignJustify as AlignJustifyIcon,
  Bold as BoldIcon, Italic as ItalicIcon, Underline as UnderlineIcon,
  Strikethrough as StrikethroughIcon, CodeIcon, Quote as QuoteIcon,
  ListIcon, ListOrdered as ListOrderedIcon, ListChecks as ListChecksIcon,
  Indent as IndentIcon, Outdent as OutdentIcon, LinkIcon, Link2 as Link2Icon,
  Unlink as UnlinkIcon, Paperclip as PaperclipIcon, Pin as PinIcon,
  PinOff as PinOffIcon, BookmarkIcon, BookmarkPlus as BookmarkPlusIcon,
  Tag as TagIcon, Tags as TagsIcon, Hash as HashIcon, At as AtIcon,
  Mention as MentionIcon, Reply as ReplyIcon, ReplyAll as ReplyAllIcon,
  Forward as ForwardIcon, SendIcon, MailIcon, Inbox as InboxIcon,
  Archive as ArchiveIcon, TrashIcon, Delete as DeleteIcon,
  EraserIcon, ScissorsIcon, CopyIcon, ClipboardIcon, ClipboardCopy as ClipboardCopyIcon,
  ClipboardPaste as ClipboardPasteIcon, ClipboardX as ClipboardXIcon,
  FileIcon, FilePlus as FilePlusIcon, FileMinus as FileMinusIcon,
  FileX as FileXIcon, FileCheck as FileCheckIcon, FileClock as FileClockIcon,
  FileCodeIcon, FileJson as FileJsonIcon, FileType as FileTypeIcon,
  FileImage as FileImageIcon, FileVideo as FileVideoIcon,
  FileAudio as FileAudioIcon, FileArchive as FileArchiveIcon,
  FileUp as FileUpIcon, FileDown as FileDownIcon, FolderIcon,
  FolderPlus as FolderPlusIcon, FolderMinus as FolderMinusIcon,
  FolderOpen as FolderOpenIcon, FolderTree as FolderTreeIcon,
  FolderCheck as FolderCheckIcon, FolderX as FolderXIcon,
  FolderClock as FolderClockIcon, FolderCode as FolderCodeIcon,
  FolderGit as FolderGitIcon, FolderGit2 as FolderGit2Icon,
  FolderKanban as FolderKanbanIcon, FolderCog as FolderCogIcon,
  FolderLock as FolderLockIcon, FolderHeart as FolderHeartIcon,
  FolderSearch as FolderSearchIcon, FolderSync as FolderSyncIcon,
  Folders as FoldersIcon, HardDrive as HardDriveIcon, DatabaseIcon,
  ServerIcon, CloudIcon, CloudUpload as CloudUploadIcon,
  CloudDownload as CloudDownloadIcon, CloudRainIcon, CloudSnowIcon,
  CloudLightning as CloudLightningIcon, CloudFog as CloudFogIcon,
  CloudSun as CloudSunIcon, CloudMoon as CloudMoonIcon,
  CloudDrizzle as CloudDrizzleIcon, Haze as HazeIcon,
  ThermometerSun as ThermometerSunIcon, ThermometerSnowflake as ThermometerSnowflakeIcon,
  DropletsIcon, Droplet as DropletIcon, Water as WaterIcon,
  Waves as WavesIcon, UmbrellaIcon, SnowflakeIcon, WindIcon,
  Tornado as TornadoIcon, Hurricane as HurricaneIcon,
  Earthquake as EarthquakeIcon, Volcano as VolcanoIcon,
  MountainIcon, MountainSnow as MountainSnowIcon, TreePineIcon,
  TreeDeciduousIcon, Flower2Icon, LeafIcon, SproutIcon,
  RecycleIcon, Trash2Icon
} from 'lucide-react'

// ── API Configuration ───────────────────────────────────────────────────────
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ── Components ──────────────────────────────────────────────────────────────

function Sidebar({ isOpen, setIsOpen }) {
  const location = useLocation()
  const menuItems = [
    { path: '/', icon: Zap, label: 'Dashboard' },
    { path: '/agents', icon: Bot, label: 'AI Agents' },
    { path: '/crews', icon: Users, label: 'Crews' },
    { path: '/chat', icon: MessageSquare, label: 'Chat' },
    { path: '/skills', icon: Brain, label: 'Skills' },
    { path: '/templates', icon: FileCode, label: 'Templates' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ]

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside className={`
        fixed lg:static inset-y-0 left-0 z-50
        w-64 bg-[#111118] border-r border-[#2a2a3a]
        transform transition-transform duration-300
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        flex flex-col
      `}>
        {/* Logo */}
        <div className="p-6 border-b border-[#2a2a3a]">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#00d4ff] to-[#7c3aed] 
                          flex items-center justify-center shadow-lg shadow-[#00d4ff]/20">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-bold text-lg text-white">AI Startup</h1>
              <p className="text-xs text-[#64748b]">Multi-Agent System</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {menuItems.map(item => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setIsOpen(false)}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium
                  transition-all duration-200
                  ${isActive 
                    ? 'bg-gradient-to-r from-[#00d4ff]/10 to-transparent text-[#00d4ff] border border-[#00d4ff]/20' 
                    : 'text-[#94a3b8] hover:text-white hover:bg-[#1a1a24]'
                  }
                `}
              >
                <Icon className="w-5 h-5" />
                {item.label}
                {isActive && <ChevronRight className="w-4 h-4 ml-auto" />}
              </Link>
            )
          })}
        </nav>

        {/* Status */}
        <div className="p-4 border-t border-[#2a2a3a]">
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-[#1a1a24]">
            <div className="w-2 h-2 rounded-full bg-[#10b981] animate-pulse" />
            <span className="text-sm text-[#94a3b8]">System Online</span>
            <span className="text-xs text-[#64748b] ml-auto">Groq API</span>
          </div>
        </div>
      </aside>
    </>
  )
}

function Header({ setSidebarOpen }) {
  return (
    <header className="h-16 bg-[#111118]/80 backdrop-blur-xl border-b border-[#2a2a3a]
                     flex items-center justify-between px-6 sticky top-0 z-30">
      <button 
        onClick={() => setSidebarOpen(true)}
        className="lg:hidden p-2 rounded-lg hover:bg-[#1a1a24] transition-colors"
      >
        <Menu className="w-5 h-5" />
      </button>

      <div className="flex items-center gap-4 ml-auto">
        <button className="p-2 rounded-lg hover:bg-[#1a1a24] transition-colors relative">
          <Bell className="w-5 h-5 text-[#94a3b8]" />
          <span className="absolute top-1 right-1 w-2 h-2 bg-[#ef4444] rounded-full" />
        </button>
        <div className="flex items-center gap-3 pl-4 border-l border-[#2a2a3a]">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#00d4ff] to-[#7c3aed] 
                        flex items-center justify-center text-sm font-bold">
            AI
          </div>
          <span className="text-sm font-medium hidden sm:block">Admin</span>
        </div>
      </div>
    </header>
  )
}

// ── Dashboard Page ──────────────────────────────────────────────────────────

function Dashboard() {
  const [stats, setStats] = useState({
    activeAgents: 0,
    totalTasks: 0,
    completedTasks: 0,
    apiCalls: 0
  })

  useEffect(() => {
    fetch(`${API_BASE}/`)
      .then(r => r.json())
      .then(data => {
        setStats({
          activeAgents: 3,
          totalTasks: 156,
          completedTasks: 142,
          apiCalls: 2847
        })
      })
      .catch(() => {
        setStats({
          activeAgents: 3,
          totalTasks: 156,
          completedTasks: 142,
          apiCalls: 2847
        })
      })
  }, [])

  const statCards = [
    { label: 'Active Agents', value: stats.activeAgents, icon: Bot, color: '#00d4ff', trend: '+12%' },
    { label: 'Total Tasks', value: stats.totalTasks, icon: Layers, color: '#7c3aed', trend: '+8%' },
    { label: 'Completed', value: stats.completedTasks, icon: CheckCircle, color: '#10b981', trend: '+15%' },
    { label: 'API Calls', value: stats.apiCalls.toLocaleString(), icon: Zap, color: '#f59e0b', trend: '+23%' },
  ]

  const recentActivity = [
    { id: 1, type: 'crew', name: 'Startup Ideation Crew', status: 'completed', time: '2 min ago' },
    { id: 2, type: 'agent', name: 'Market Researcher', status: 'running', time: '5 min ago' },
    { id: 3, type: 'crew', name: 'Code Review Crew', status: 'completed', time: '12 min ago' },
    { id: 4, type: 'agent', name: 'SEO Specialist', status: 'idle', time: '20 min ago' },
  ]

  return (
    <div className="p-6 space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Dashboard</h2>
          <p className="text-[#94a3b8] mt-1">Welcome back to your AI Army Command Center</p>
        </div>
        <Link to="/crews/create" className="btn-primary">
          <Plus className="w-4 h-4" />
          New Crew
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((card, i) => {
          const Icon = card.icon
          return (
            <div key={i} className="card group">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-[#94a3b8] text-sm">{card.label}</p>
                  <p className="text-2xl font-bold text-white mt-1">{card.value}</p>
                </div>
                <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                     style={{ background: `${card.color}15` }}>
                  <Icon className="w-5 h-5" style={{ color: card.color }} />
                </div>
              </div>
              <div className="flex items-center gap-2 mt-4">
                <TrendingUp className="w-3 h-3 text-[#10b981]" />
                <span className="text-xs text-[#10b981] font-medium">{card.trend}</span>
                <span className="text-xs text-[#64748b]">vs last week</span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2 card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#00d4ff]" />
              Recent Activity
            </h3>
            <button className="text-sm text-[#00d4ff] hover:underline">View All</button>
          </div>
          <div className="space-y-3">
            {recentActivity.map(item => (
              <div key={item.id} 
                   className="flex items-center gap-4 p-3 rounded-xl bg-[#1a1a24] hover:bg-[#222230] transition-colors">
                <div className={`w-10 h-10 rounded-xl flex items-center justify-center
                  ${item.status === 'completed' ? 'bg-[#10b981]/15' : 
                    item.status === 'running' ? 'bg-[#f59e0b]/15' : 'bg-[#64748b]/15'}`}>
                  {item.type === 'crew' ? <Users className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-white">{item.name}</p>
                  <p className="text-xs text-[#64748b]">{item.type === 'crew' ? 'Crew' : 'Agent'} - {item.time}</p>
                </div>
                <span className={`badge ${
                  item.status === 'completed' ? 'badge-success' :
                  item.status === 'running' ? 'badge-warning' : 'badge-info'
                }`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-[#f59e0b]" />
            Quick Actions
          </h3>
          <div className="space-y-3">
            <Link to="/crews/create" className="flex items-center gap-3 p-3 rounded-xl bg-[#1a1a24] 
              hover:bg-[#222230] transition-colors group">
              <div className="w-10 h-10 rounded-xl bg-[#00d4ff]/15 flex items-center justify-center
                            group-hover:scale-110 transition-transform">
                <Users className="w-5 h-5 text-[#00d4ff]" />
              </div>
              <div>
                <p className="text-sm font-medium text-white">Create Crew</p>
                <p className="text-xs text-[#64748b]">Launch multi-agent team</p>
              </div>
            </Link>
            <Link to="/chat" className="flex items-center gap-3 p-3 rounded-xl bg-[#1a1a24] 
              hover:bg-[#222230] transition-colors group">
              <div className="w-10 h-10 rounded-xl bg-[#7c3aed]/15 flex items-center justify-center
                            group-hover:scale-110 transition-transform">
                <MessageSquare className="w-5 h-5 text-[#7c3aed]" />
              </div>
              <div>
                <p className="text-sm font-medium text-white">AI Chat</p>
                <p className="text-xs text-[#64748b]">Talk with Groq models</p>
              </div>
            </Link>
            <Link to="/templates" className="flex items-center gap-3 p-3 rounded-xl bg-[#1a1a24] 
              hover:bg-[#222230] transition-colors group">
              <div className="w-10 h-10 rounded-xl bg-[#10b981]/15 flex items-center justify-center
                            group-hover:scale-110 transition-transform">
                <FileCode className="w-5 h-5 text-[#10b981]" />
              </div>
              <div>
                <p className="text-sm font-medium text-white">Use Template</p>
                <p className="text-xs text-[#64748b]">Pre-built agent crews</p>
              </div>
            </Link>
            <Link to="/skills" className="flex items-center gap-3 p-3 rounded-xl bg-[#1a1a24] 
              hover:bg-[#222230] transition-colors group">
              <div className="w-10 h-10 rounded-xl bg-[#f59e0b]/15 flex items-center justify-center
                            group-hover:scale-110 transition-transform">
                <Brain className="w-5 h-5 text-[#f59e0b]" />
              </div>
              <div>
                <p className="text-sm font-medium text-white">Manage Skills</p>
                <p className="text-xs text-[#64748b]">10 Fable 5 skills</p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── AI Agents Page ──────────────────────────────────────────────────────────

function AgentsPage() {
  const [agents, setAgents] = useState([
    { id: 1, name: 'Market Researcher', role: 'Market Research Specialist', 
      goal: 'Identify market gaps and opportunities', status: 'idle', model: 'llama-3.3-70b' },
    { id: 2, name: 'Product Strategist', role: 'Product Strategy Expert',
      goal: 'Define product vision and roadmap', status: 'running', model: 'llama-3.3-70b' },
    { id: 3, name: 'Tech Architect', role: 'Technical Architect',
      goal: 'Design scalable technical architecture', status: 'idle', model: 'llama-3.1-8b' },
    { id: 4, name: 'Code Reviewer', role: 'Senior Code Reviewer',
      goal: 'Identify bugs and code smells', status: 'completed', model: 'compound-beta' },
    { id: 5, name: 'SEO Specialist', role: 'SEO Expert',
      goal: 'Optimize content for search engines', status: 'idle', model: 'llama-3.1-8b' },
  ])

  const [showCreate, setShowCreate] = useState(false)
  const [newAgent, setNewAgent] = useState({
    name: '', role: '', goal: '', backstory: '', model: 'llama-3.3-70b'
  })

  const models = [
    { id: 'llama-3.3-70b', name: 'Llama 3.3 70B', desc: 'Best for complex reasoning' },
    { id: 'llama-3.1-8b', name: 'Llama 3.1 8B', desc: 'Fast and efficient' },
    { id: 'compound-beta', name: 'Compound Beta', desc: 'Advanced reasoning' },
    { id: 'llama-4-scout', name: 'Llama 4 Scout', desc: 'Latest model' },
  ]

  const handleCreate = () => {
    if (!newAgent.name || !newAgent.role) return
    setAgents([...agents, { ...newAgent, id: Date.now(), status: 'idle' }])
    setNewAgent({ name: '', role: '', goal: '', backstory: '', model: 'llama-3.3-70b' })
    setShowCreate(false)
  }

  return (
    <div className="p-6 space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">AI Agents</h2>
          <p className="text-[#94a3b8] mt-1">Manage your intelligent agent workforce</p>
        </div>
        <button onClick={() => setShowCreate(true)} className="btn-primary">
          <Plus className="w-4 h-4" />
          Create Agent
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {agents.map(agent => (
          <div key={agent.id} className="card group hover:border-[#00d4ff]/30">
            <div className="flex items-start justify-between mb-3">
              <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#00d4ff]/20 to-[#7c3aed]/20 
                            flex items-center justify-center">
                <Bot className="w-6 h-6 text-[#00d4ff]" />
              </div>
              <span className={`badge ${
                agent.status === 'idle' ? 'badge-info' :
                agent.status === 'running' ? 'badge-warning' : 'badge-success'
              }`}>
                <span className={`status-dot ${agent.status === 'running' ? 'busy' : 
                  agent.status === 'completed' ? 'online' : 'offline'} mr-1`} />
                {agent.status}
              </span>
            </div>
            <h3 className="font-semibold text-white text-lg">{agent.name}</h3>
            <p className="text-sm text-[#94a3b8] mt-1">{agent.role}</p>
            <p className="text-xs text-[#64748b] mt-2 line-clamp-2">{agent.goal}</p>
            <div className="flex items-center gap-2 mt-4 pt-4 border-t border-[#2a2a3a]">
              <Cpu className="w-4 h-4 text-[#64748b]" />
              <span className="text-xs text-[#64748b]">{agent.model}</span>
            </div>
          </div>
        ))}
      </div>

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#111118] border border-[#2a2a3a] rounded-2xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Create New Agent</h3>
              <button onClick={() => setShowCreate(false)} className="p-2 hover:bg-[#1a1a24] rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-[#94a3b8] mb-2 block">Agent Name</label>
                <input className="input-field" placeholder="e.g., Market Researcher"
                  value={newAgent.name} onChange={e => setNewAgent({...newAgent, name: e.target.value})} />
              </div>
              <div>
                <label className="text-sm text-[#94a3b8] mb-2 block">Role</label>
                <input className="input-field" placeholder="e.g., Market Research Specialist"
                  value={newAgent.role} onChange={e => setNewAgent({...newAgent, role: e.target.value})} />
              </div>
              <div>
                <label className="text-sm text-[#94a3b8] mb-2 block">Goal</label>
                <textarea className="textarea-field" placeholder="What should this agent achieve?"
                  value={newAgent.goal} onChange={e => setNewAgent({...newAgent, goal: e.target.value})} />
              </div>
              <div>
                <label className="text-sm text-[#94a3b8] mb-2 block">Backstory</label>
                <textarea className="textarea-field" placeholder="Agent background and expertise..."
                  value={newAgent.backstory} onChange={e => setNewAgent({...newAgent, backstory: e.target.value})} />
              </div>
              <div>
                <label className="text-sm text-[#94a3b8] mb-2 block">Model</label>
                <select className="select-field" value={newAgent.model}
                  onChange={e => setNewAgent({...newAgent, model: e.target.value})}>
                  {models.map(m => <option key={m.id} value={m.id}>{m.name} - {m.desc}</option>)}
                </select>
              </div>
              <button onClick={handleCreate} className="btn-primary w-full justify-center mt-4">
                <Bot className="w-4 h-4" />
                Create Agent
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Crews Page ────────────────────────────────────────────────────────────────

function CrewsPage() {
  const [crews, setCrews] = useState([
    { id: 'crew-1', name: 'Startup Ideation Crew', status: 'completed', 
      agents: 3, tasks: 3, progress: 100 },
    { id: 'crew-2', name: 'Code Review Crew', status: 'running',
      agents: 3, tasks: 3, progress: 67 },
    { id: 'crew-3', name: 'Content Creation Crew', status: 'pending',
      agents: 3, tasks: 3, progress: 0 },
  ])

  return (
    <div className="p-6 space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Crews</h2>
          <p className="text-[#94a3b8] mt-1">Multi-agent orchestration teams</p>
        </div>
        <Link to="/crews/create" className="btn-primary">
          <Plus className="w-4 h-4" />
          New Crew
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {crews.map(crew => (
          <div key={crew.id} className="card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="font-semibold text-white text-lg">{crew.name}</h3>
                <div className="flex items-center gap-4 mt-2 text-sm text-[#64748b]">
                  <span className="flex items-center gap-1">
                    <Users className="w-4 h-4" /> {crew.agents} agents
                  </span>
                  <span className="flex items-center gap-1">
                    <Layers className="w-4 h-4" /> {crew.tasks} tasks
                  </span>
                </div>
              </div>
              <span className={`badge ${
                crew.status === 'completed' ? 'badge-success' :
                crew.status === 'running' ? 'badge-warning' : 'badge-info'
              }`}>
                {crew.status}
              </span>
            </div>

            <div className="mt-4">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="text-[#94a3b8]">Progress</span>
                <span className="text-white font-medium">{crew.progress}%</span>
              </div>
              <div className="h-2 bg-[#1a1a24] rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all duration-500"
                  style={{ 
                    width: `${crew.progress}%`,
                    background: crew.status === 'completed' ? 'var(--success)' :
                               crew.status === 'running' ? 'var(--warning)' : 'var(--primary)'
                  }}
                />
              </div>
            </div>

            <div className="flex gap-2 mt-4">
              <button className="btn-secondary text-xs py-2 px-4">
                <Eye className="w-3 h-3" />
                View
              </button>
              {crew.status === 'running' && (
                <button className="btn-secondary text-xs py-2 px-4">
                  <Pause className="w-3 h-3" />
                  Pause
                </button>
              )}
              <button className="btn-secondary text-xs py-2 px-4 ml-auto">
                <RotateCcw className="w-3 h-3" />
                Restart
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Chat Page ─────────────────────────────────────────────────────────────────

function ChatPage() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I am your AI assistant powered by Groq. How can I help you today?' }
  ])
  const [input, setInput] = useState('')
  const [model, setModel] = useState('llama-3.3-70b')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const models = [
    { id: 'llama-3.3-70b', name: 'Llama 3.3 70B' },
    { id: 'llama-3.1-8b', name: 'Llama 3.1 8B' },
    { id: 'compound-beta', name: 'Compound Beta' },
    { id: 'llama-4-scout', name: 'Llama 4 Scout' },
    { id: 'qwen3-32b', name: 'Qwen3 32B' },
  ]

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage].map(m => ({ role: m.role, content: m.content })),
          model,
          temperature: 0.7,
          max_tokens: 2048
        })
      })

      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.content }])
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please check your connection to the backend server.' 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] animate-fadeIn">
      <div className="h-14 border-b border-[#2a2a3a] flex items-center justify-between px-6 bg-[#111118]/80 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <MessageSquare className="w-5 h-5 text-[#00d4ff]" />
          <span className="font-semibold text-white">AI Chat</span>
        </div>
        <select className="select-field w-auto text-xs py-2" value={model}
          onChange={e => setModel(e.target.value)}>
          {models.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
        </select>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
              ${msg.role === 'user' 
                ? 'bg-gradient-to-br from-[#7c3aed] to-[#00d4ff]' 
                : 'bg-gradient-to-br from-[#00d4ff] to-[#7c3aed]'
              }`}>
              {msg.role === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
            </div>
            <div className={`max-w-[80%] p-4 rounded-2xl ${
              msg.role === 'user'
                ? 'bg-gradient-to-br from-[#7c3aed]/20 to-[#00d4ff]/20 border border-[#7c3aed]/30'
                : 'bg-[#1a1a24] border border-[#2a2a3a]'
            }`}>
              <p className="text-sm text-white whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#00d4ff] to-[#7c3aed] flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-[#1a1a24] border border-[#2a2a3a] rounded-2xl p-4">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 text-[#00d4ff] animate-spin" />
                <span className="text-sm text-[#94a3b8]">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-[#2a2a3a] bg-[#111118]/80 backdrop-blur-xl">
        <div className="flex gap-3">
          <input className="input-field flex-1" placeholder="Type your message..."
            value={input} onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()} />
          <button onClick={handleSend} disabled={isLoading || !input.trim()} className="btn-primary px-4">
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Skills Page (10 Fable 5 Skills) ─────────────────────────────────────────

function SkillsPage() {
  const [skills] = useState([
    {
      id: 'act-when-ready',
      name: 'Act When Ready',
      description: 'Stop over-planning and re-deriving settled facts. Take action when you have enough information.',
      category: 'Efficiency',
      icon: Zap,
      color: '#00d4ff',
      rules: [
        'Take action when you have enough information — sufficiency, not completeness',
        'Facts already established are settled — do not re-verify or re-summarize',
        'Decisions the user already made are closed — do not reopen them',
        'Planning text should be at most a few lines',
        'Deliberate internally as deeply as needed, but act in output'
      ]
    },
    {
      id: 'autonomous-continuation',
      name: 'Autonomous Continuation',
      description: 'Keep running to completion in unattended pipelines without stopping on intent statements.',
      category: 'Automation',
      icon: Play,
      color: '#10b981',
      rules: [
        'Operate without human in the loop — questions cannot be answered mid-run',
        'For reversible actions within scope, proceed without asking',
        'Stop only for: irreversible actions, scope changes, or missing user-only input',
        'Before ending any turn: if final paragraph is a plan or promise, execute first',
        'Do not propose new sessions on account of context limits'
      ]
    },
    {
      id: 'effort-calibrator',
      name: 'Effort Calibrator',
      description: 'Choose the right effort level trading intelligence against latency and cost.',
      category: 'Optimization',
      icon: BarChart3,
      color: '#7c3aed',
      rules: [
        'Routine transforms: medium (or low if latency matters)',
        'Most analysis and writing: high (general default)',
        'Coding and agentic work: high — escalate to xhigh only for capability-sensitive tasks',
        'Hardest work (large migrations, novel research): xhigh',
        'max is rarely right — significant cost for small gains'
      ]
    },
    {
      id: 'grounded-progress',
      name: 'Grounded Progress',
      description: 'Make progress reports verifiable against actual tool results during long runs.',
      category: 'Reliability',
      icon: CheckCircle,
      color: '#10b981',
      rules: [
        'Before any progress claim, bind it to a tool result from this session',
        'Completed — name the command/test whose output proves it',
        'Failed — say so, include relevant output verbatim',
        'Skipped — state it as skipped with reason',
        'Not yet verified — label explicitly as unverified'
      ]
    },
    {
      id: 'markdown-memory',
      name: 'Markdown Memory',
      description: 'File-based lesson memory that persists across sessions for recurring agents.',
      category: 'Memory',
      icon: BookMarked,
      color: '#f59e0b',
      rules: [
        'One lesson per file — update existing, never create near-duplicates',
        'Line 1: one-sentence summary that makes sense without opening the file',
        'Body: what happened, correct approach, and why it mattered',
        'Do not record what repo/docs/chat history already state',
        'Delete lessons proven wrong — wrong notes do more damage than missing ones'
      ]
    },
    {
      id: 'no-gold-plating',
      name: 'No Gold-Plating',
      description: 'Keep changes minimal — no unrequested refactors, abstractions, or feature creep.',
      category: 'Code Quality',
      icon: Scissors,
      color: '#ef4444',
      rules: [
        'Diff should map one-to-one to the request',
        'No helpers or abstractions for a single call site — inline it',
        'Do not design for requirements that do not exist yet',
        'Validate only at system boundaries — trust framework inside',
        'If adjacent work seems valuable, note it in one sentence at the end — do not do it'
      ]
    },
    {
      id: 'regrounding-summary',
      name: 'Re-grounding Summary',
      description: 'Make final reports readable to someone who saw none of the work.',
      category: 'Communication',
      icon: FileText,
      color: '#00d4ff',
      rules: [
        'Open with the outcome: one sentence answering what happened',
        'Complete sentences — no arrow chains, no invented abbreviations',
        'Never reference working notes as if reader saw them',
        'Identifiers get their own plain-language clause: what it is, why it matters',
        'Close with what is needed from the reader, if anything'
      ]
    },
    {
      id: 'scope-guard',
      name: 'Scope Guard',
      description: 'Prevent unrequested actions — diagnose when asked, do not apply fixes without permission.',
      category: 'Safety',
      icon: Shield,
      color: '#ef4444',
      rules: [
        'Problem description — deliverable is assessment only, do not apply fixes',
        'Explicit change request — act within named scope',
        'Ambiguous — treat as assessment-only, say what you would do next if asked',
        'State-changing actions need evidence supporting this specific action',
        'No side-deliverables: emails, tickets, branches, README updates, TODO files'
      ]
    },
    {
      id: 'skill-refactorer',
      name: 'Skill Refactorer',
      description: 'Audit and rewrite skills for Fable 5 — remove obsolete scaffolding, keep guardrails.',
      category: 'Migration',
      icon: RefreshCw,
      color: '#7c3aed',
      rules: [
        'Inventory every imperative instruction as a separate line item',
        'Classify: Guardrail (keep), Preference (keep, compress), Compensation (delete)',
        'For deleted compensation: state the outcome once, not the procedure',
        'Tighten description field — triggering logic stays in frontmatter',
        'Refactored skill should be 30-60% shorter — if not, re-run classification'
      ]
    },
    {
      id: 'subagent-orchestration',
      name: 'Subagent Orchestration',
      description: 'Delegate work to parallel subagents with proper coordination and fresh-context verifiers.',
      category: 'Orchestration',
      icon: GitBranch,
      color: '#10b981',
      rules: [
        'Delegate when: independent, large enough to amortize handoff, specifiable in a few sentences',
        'Launch independent subagents in same turn, keep working while they run',
        'Intervene only on signal: off-track or missing context',
        'Fresh-context verifiers outperform self-critique — give spec and output, not reasoning',
        'Good brief: goal, inputs, definition of done, constraints, where to write results'
      ]
    }
  ])

  const [selectedSkill, setSelectedSkill] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')

  const filteredSkills = skills.filter(s => 
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.category.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="p-6 space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Fable 5 Skills</h2>
          <p className="text-[#94a3b8] mt-1">10 native agent skills for Claude Fable 5</p>
        </div>
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#64748b]" />
          <input className="input-field pl-10 w-64" placeholder="Search skills..."
            value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {filteredSkills.map(skill => {
          const Icon = skill.icon
          return (
            <div key={skill.id} onClick={() => setSelectedSkill(skill)}
              className="card cursor-pointer group hover:border-[#00d4ff]/30 transition-all">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
                  style={{ background: `${skill.color}15` }}>
                  <Icon className="w-6 h-6" style={{ color: skill.color }} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-white">{skill.name}</h3>
                    <span className="text-[10px] px-2 py-0.5 rounded-full font-medium"
                      style={{ background: `${skill.color}15`, color: skill.color }}>
                      {skill.category}
                    </span>
                  </div>
                  <p className="text-sm text-[#94a3b8] mt-1 line-clamp-2">{skill.description}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 mt-4 text-xs text-[#64748b]">
                <span>{skill.rules.length} rules</span>
                <ChevronRight className="w-3 h-3 ml-auto group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          )
        })}
      </div>

      {selectedSkill && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#111118] border border-[#2a2a3a] rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl flex items-center justify-center"
                  style={{ background: `${selectedSkill.color}15` }}>
                  <selectedSkill.icon className="w-7 h-7" style={{ color: selectedSkill.color }} />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white">{selectedSkill.name}</h3>
                  <span className="text-xs px-2 py-0.5 rounded-full font-medium"
                    style={{ background: `${selectedSkill.color}15`, color: selectedSkill.color }}>
                    {selectedSkill.category}
                  </span>
                </div>
              </div>
              <button onClick={() => setSelectedSkill(null)} className="p-2 hover:bg-[#1a1a24] rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-[#94a3b8] mb-6">{selectedSkill.description}</p>

            <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#00d4ff]" />
              Operating Rules
            </h4>
            <div className="space-y-3">
              {selectedSkill.rules.map((rule, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-[#1a1a24]">
                  <span className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                    style={{ background: `${selectedSkill.color}15`, color: selectedSkill.color }}>
                    {i + 1}
                  </span>
                  <p className="text-sm text-[#e2e8f0]">{rule}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-6 border-t border-[#2a2a3a]">
              <button onClick={() => setSelectedSkill(null)} className="btn-secondary w-full justify-center">
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Templates Page ──────────────────────────────────────────────────────────

function TemplatesPage() {
  const [templates] = useState([
    {
      id: 'startup_ideation',
      name: 'Startup Ideation Crew',
      description: 'Generate and validate startup ideas with market research, product strategy, and technical architecture.',
      agents: 3,
      tasks: 3,
      icon: Zap,
      color: '#00d4ff'
    },
    {
      id: 'code_review',
      name: 'AI Code Review Crew',
      description: 'Automated code review with bug detection, performance optimization, and security auditing.',
      agents: 3,
      tasks: 3,
      icon: Code,
      color: '#10b981'
    },
    {
      id: 'content_creation',
      name: 'Content Creation Crew',
      description: 'AI-powered content creation with strategy, copywriting, and SEO optimization.',
      agents: 3,
      tasks: 3,
      icon: FileText,
      color: '#f59e0b'
    }
  ])

  const [selectedTemplate, setSelectedTemplate] = useState(null)

  return (
    <div className="p-6 space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Crew Templates</h2>
          <p className="text-[#94a3b8] mt-1">Pre-built multi-agent teams ready to deploy</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {templates.map(template => {
          const Icon = template.icon
          return (
            <div key={template.id} className="card group">
              <div className="w-14 h-14 rounded-xl flex items-center justify-center mb-4"
                style={{ background: `${template.color}15` }}>
                <Icon className="w-7 h-7" style={{ color: template.color }} />
              </div>
              <h3 className="font-semibold text-white text-lg">{template.name}</h3>
              <p className="text-sm text-[#94a3b8] mt-2">{template.description}</p>
              <div className="flex items-center gap-4 mt-4 text-xs text-[#64748b]">
                <span className="flex items-center gap-1">
                  <Users className="w-3 h-3" /> {template.agents} agents
                </span>
                <span className="flex items-center gap-1">
                  <Layers className="w-3 h-3" /> {template.tasks} tasks
                </span>
              </div>
              <button onClick={() => setSelectedTemplate(template)}
                className="btn-primary w-full justify-center mt-4">
                <Play className="w-4 h-4" />
                Use Template
              </button>
            </div>
          )
        })}
      </div>

      {selectedTemplate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#111118] border border-[#2a2a3a] rounded-2xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-start justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 rounded-xl flex items-center justify-center"
                  style={{ background: `${selectedTemplate.color}15` }}>
                  <selectedTemplate.icon className="w-7 h-7" style={{ color: selectedTemplate.color }} />
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-white">{selectedTemplate.name}</h3>
                  <p className="text-sm text-[#94a3b8]">{selectedTemplate.description}</p>
                </div>
              </div>
              <button onClick={() => setSelectedTemplate(null)} className="p-2 hover:bg-[#1a1a24] rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-[#1a1a24]">
                <h4 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <Users className="w-4 h-4 text-[#00d4ff]" />
                  Agents
                </h4>
                <div className="space-y-2">
                  {selectedTemplate.id === 'startup_ideation' && (
                    <>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-[#111118]">
                        <Bot className="w-5 h-5 text-[#00d4ff]" />
                        <div>
                          <p className="text-sm font-medium text-white">Market Researcher</p>
                          <p className="text-xs text-[#64748b]">Market Research Specialist</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-[#111118]">
                        <Bot className="w-5 h-5 text-[#7c3aed]" />
                        <div>
                          <p className="text-sm font-medium text-white">Product Strategist</p>
                          <p className="text-xs text-[#64748b]">Product Strategy Expert</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-[#111118]">
                        <Bot className="w-5 h-5 text-[#10b981]" />
                        <div>
                          <p className="text-sm font-medium text-white">Tech Architect</p>
                          <p className="text-xs text-[#64748b]">Technical Architect</p>
                        </div>
                      </div>
                    </>
                  )}
                  {selectedTemplate.id === 'code_review' && (
                    <>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-[#111118]">
                        <Bot className="w-5 h-5 text-[#ef4444]" />
                        <div>
                          <p className="text-sm font-medium text-white">Code Reviewer</p>
                          <p className="text-xs text-[#64748b]">Senior Code Reviewer</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-[#111118]">
                        <Bot className="w-5 h-5 text-[#f59e0b]" />
                        <div>
                          <p className="text-sm font-medium text-white">Performance Optimizer</p>
                          <p className="text-xs text-[#64748b]">Performance Engineer</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-[#111118]">
                        <Bot className="w-5 h-5 text-[#00d4ff]" />
                        <div>
                          <p className="text-sm font-medium text-white">Security Auditor</p>
                          <p className="text-xs text-[#64748b]">Security Expert</p>
                        </div>
                      </div>
                    </>
                  )}
                  {selectedTemplate.id === 'content_creation' && (
                    <>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-[#111118]">
                        <Bot className="w-5 h-5 text-[#7c3aed]" />
                        <div>
                          <p className="text-sm font-medium text-white">Content Strategist</p>
                          <p className="text-xs text-[#64748b]">Content Strategy Expert</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-[#111118]">
                        <Bot className="w-5 h-5 text-[#00d4ff]" />
                        <div>
                          <p className="text-sm font-medium text-white">Copywriter</p>
                          <p className="text-xs text-[#64748b]">Professional Copywriter</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-[#111118]">
                        <Bot className="w-5 h-5 text-[#10b981]" />
                        <div>
                          <p className="text-sm font-medium text-white">SEO Specialist</p>
                          <p className="text-xs text-[#64748b]">SEO Expert</p>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button className="btn-primary flex-1 justify-center">
                <Play className="w-4 h-4" />
                Deploy Crew
              </button>
              <button onClick={() => setSelectedTemplate(null)} className="btn-secondary flex-1 justify-center">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ── Analytics Page ──────────────────────────────────────────────────────────

function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('7d')

  const metrics = [
    { label: 'Total API Calls', value: '12,847', change: '+23%', positive: true },
    { label: 'Avg Response Time', value: '142ms', change: '-18%', positive: true },
    { label: 'Success Rate', value: '98.7%', change: '+2.1%', positive: true },
    { label: 'Active Sessions', value: '47', change: '+12', positive: true },
  ]

  const agentPerformance = [
    { name: 'Market Researcher', tasks: 45, success: 98, avgTime: '2.3m' },
    { name: 'Product Strategist', tasks: 38, success: 95, avgTime: '3.1m' },
    { name: 'Tech Architect', tasks: 32, success: 97, avgTime: '4.2m' },
    { name: 'Code Reviewer', tasks: 67, success: 99, avgTime: '1.8m' },
    { name: 'SEO Specialist', tasks: 28, success: 94, avgTime: '2.7m' },
  ]

  return (
    <div className="p-6 space-y-6 animate-fadeIn">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Analytics</h2>
          <p className="text-[#94a3b8] mt-1">Performance metrics and insights</p>
        </div>
        <div className="flex gap-2">
          {['24h', '7d', '30d', '90d'].map(range => (
            <button key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                timeRange === range 
                  ? 'bg-[#00d4ff]/15 text-[#00d4ff] border border-[#00d4ff]/30' 
                  : 'bg-[#1a1a24] text-[#94a3b8] border border-[#2a2a3a] hover:border-[#00d4ff]/30'
              }`}>
              {range}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, i) => (
          <div key={i} className="card">
            <p className="text-sm text-[#94a3b8]">{metric.label}</p>
            <p className="text-2xl font-bold text-white mt-1">{metric.value}</p>
            <div className="flex items-center gap-1 mt-2">
              <TrendingUp className={`w-3 h-3 ${metric.positive ? 'text-[#10b981]' : 'text-[#ef4444]'}`} />
              <span className={`text-xs font-medium ${metric.positive ? 'text-[#10b981]' : 'text-[#ef4444]'}`}>
                {metric.change}
              </span>
              <span className="text-xs text-[#64748b]">vs last period</span>
            </div>
          </div>
        ))}
      </div>

      <div className="card">
        <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
          <BarChart3 className="w-5 h-5 text-[#00d4ff]" />
          Agent Performance
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-xs text-[#64748b] uppercase tracking-wider">
                <th className="pb-3 pr-4">Agent</th>
                <th className="pb-3 pr-4">Tasks Completed</th>
                <th className="pb-3 pr-4">Success Rate</th>
                <th className="pb-3">Avg Time</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {agentPerformance.map((agent, i) => (
                <tr key={i} className="border-t border-[#2a2a3a]">
                  <td className="py-4 pr-4">
                    <div className="flex items-center gap-3">
                      <Bot className="w-5 h-5 text-[#00d4ff]" />
                      <span className="text-white font-medium">{agent.name}</span>
                    </div>
                  </td>
                  <td className="py-4 pr-4 text-[#94a3b8]">{agent.tasks}</td>
                  <td className="py-4 pr-4">
                    <div className="flex items-center gap-2">
                      <div className="w-20 h-2 bg-[#1a1a24] rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-[#00d4ff] to-[#10b981] rounded-full"
                          style={{ width: `${agent.success}%` }} />
                      </div>
                      <span className="text-[#94a3b8]">{agent.success}%</span>
                    </div>
                  </td>
                  <td className="py-4 text-[#94a3b8]">{agent.avgTime}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

// ── Settings Page ───────────────────────────────────────────────────────────

function SettingsPage() {
  const [settings, setSettings] = useState({
    groqApiKey: '',
    defaultModel: 'llama-3.3-70b',
    temperature: 0.7,
    maxTokens: 2048,
    autoSave: true,
    notifications: true,
    darkMode: true,
    language: 'en'
  })

  const models = [
    { id: 'llama-3.3-70b', name: 'Llama 3.3 70B' },
    { id: 'llama-3.1-8b', name: 'Llama 3.1 8B' },
    { id: 'compound-beta', name: 'Compound Beta' },
    { id: 'llama-4-scout', name: 'Llama 4 Scout' },
    { id: 'qwen3-32b', name: 'Qwen3 32B' },
    { id: 'kimi-k2', name: 'Kimi K2' },
  ]

  return (
    <div className="p-6 space-y-6 animate-fadeIn">
      <div>
        <h2 className="text-2xl font-bold text-white">Settings</h2>
        <p className="text-[#94a3b8] mt-1">Configure your AI Startup environment</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* API Configuration */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Key className="w-5 h-5 text-[#00d4ff]" />
            API Configuration
          </h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-[#94a3b8] mb-2 block">Groq API Key</label>
              <div className="relative">
                <input 
                  type="password"
                  className="input-field pr-10"
                  value={settings.groqApiKey}
                  onChange={e => setSettings({...settings, groqApiKey: e.target.value})}
                />
                <Lock className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-[#64748b]" />
              </div>
            </div>
            <div>
              <label className="text-sm text-[#94a3b8] mb-2 block">Default Model</label>
              <select className="select-field" value={settings.defaultModel}
                onChange={e => setSettings({...settings, defaultModel: e.target.value})}>
                {models.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
              </select>
            </div>
          </div>
        </div>

        {/* Model Parameters */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-[#7c3aed]" />
            Model Parameters
          </h3>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-[#94a3b8] mb-2 block">
                Temperature: <span className="text-white">{settings.temperature}</span>
              </label>
              <input 
                type="range" min="0" max="2" step="0.1"
                value={settings.temperature}
                onChange={e => setSettings({...settings, temperature: parseFloat(e.target.value)})}
                className="w-full accent-[#00d4ff]"
              />
            </div>
            <div>
              <label className="text-sm text-[#94a3b8] mb-2 block">
                Max Tokens: <span className="text-white">{settings.maxTokens}</span>
              </label>
              <input 
                type="range" min="256" max="8192" step="256"
                value={settings.maxTokens}
                onChange={e => setSettings({...settings, maxTokens: parseInt(e.target.value)})}
                className="w-full accent-[#00d4ff]"
              />
            </div>
          </div>
        </div>

        {/* Preferences */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5 text-[#f59e0b]" />
            Preferences
          </h3>
          <div className="space-y-4">
            {[
              { key: 'autoSave', label: 'Auto-save conversations', icon: Save },
              { key: 'notifications', label: 'Enable notifications', icon: Bell },
              { key: 'darkMode', label: 'Dark mode', icon: Moon },
            ].map(pref => {
              const Icon = pref.icon
              return (
                <div key={pref.key} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Icon className="w-4 h-4 text-[#64748b]" />
                    <span className="text-sm text-[#e2e8f0]">{pref.label}</span>
                  </div>
                  <button 
                    onClick={() => setSettings({...settings, [pref.key]: !settings[pref.key]})}
                    className={`w-11 h-6 rounded-full transition-colors relative ${
                      settings[pref.key] ? 'bg-[#00d4ff]' : 'bg-[#2a2a3a]'
                    }`}>
                    <div className={`w-4 h-4 rounded-full bg-white absolute top-1 transition-transform ${
                      settings[pref.key] ? 'translate-x-6' : 'translate-x-1'
                    }`} />
                  </button>
                </div>
              )
            })}
          </div>
        </div>

        {/* System Info */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Server className="w-5 h-5 text-[#10b981]" />
            System Information
          </h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-[#94a3b8]">Version</span>
              <span className="text-white">1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#94a3b8]">Backend</span>
              <span className="text-white">FastAPI + Groq</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#94a3b8]">Frontend</span>
              <span className="text-white">React + Vite</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#94a3b8]">Models Available</span>
              <span className="text-white">6</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[#94a3b8]">Skills Loaded</span>
              <span className="text-white">10 Fable 5 Skills</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-3">
        <button className="btn-secondary">Reset to Defaults</button>
        <button className="btn-primary">
          <Save className="w-4 h-4" />
          Save Changes
        </button>
      </div>
    </div>
  )
}

// ── Create Crew Page ────────────────────────────────────────────────────────

function CreateCrewPage() {
  const [crewName, setCrewName] = useState('')
  const [agents, setAgents] = useState([
    { name: '', role: '', goal: '', backstory: '', model: 'llama-3.3-70b' }
  ])
  const [tasks, setTasks] = useState([
    { description: '', expected_output: '', agent_name: '' }
  ])
  const [process, setProcess] = useState('sequential')

  const models = [
    { id: 'llama-3.3-70b', name: 'Llama 3.3 70B' },
    { id: 'llama-3.1-8b', name: 'Llama 3.1 8B' },
    { id: 'compound-beta', name: 'Compound Beta' },
    { id: 'llama-4-scout', name: 'Llama 4 Scout' },
  ]

  const addAgent = () => {
    setAgents([...agents, { name: '', role: '', goal: '', backstory: '', model: 'llama-3.3-70b' }])
  }

  const removeAgent = (index) => {
    if (agents.length > 1) setAgents(agents.filter((_, i) => i !== index))
  }

  const addTask = () => {
    setTasks([...tasks, { description: '', expected_output: '', agent_name: '' }])
  }

  const removeTask = (index) => {
    if (tasks.length > 1) setTasks(tasks.filter((_, i) => i !== index))
  }

  const handleSubmit = async () => {
    try {
      const response = await fetch(`${API_BASE}/crew/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: crewName,
          agents,
          tasks,
          process
        })
      })
      const data = await response.json()
      alert(`Crew created! ID: ${data.crew_id}`)
    } catch (error) {
      alert('Error creating crew. Please check backend connection.')
    }
  }

  return (
    <div className="p-6 space-y-6 animate-fadeIn">
      <div>
        <h2 className="text-2xl font-bold text-white">Create New Crew</h2>
        <p className="text-[#94a3b8] mt-1">Configure your multi-agent team</p>
      </div>

      <div className="space-y-6">
        {/* Crew Info */}
        <div className="card">
          <h3 className="font-semibold text-white mb-4">Crew Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm text-[#94a3b8] mb-2 block">Crew Name</label>
              <input className="input-field" placeholder="e.g., Startup Ideation Crew"
                value={crewName} onChange={e => setCrewName(e.target.value)} />
            </div>
            <div>
              <label className="text-sm text-[#94a3b8] mb-2 block">Process Type</label>
              <select className="select-field" value={process} onChange={e => setProcess(e.target.value)}>
                <option value="sequential">Sequential</option>
                <option value="parallel">Parallel</option>
                <option value="hierarchical">Hierarchical</option>
              </select>
            </div>
          </div>
        </div>

        {/* Agents */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Bot className="w-5 h-5 text-[#00d4ff]" />
              Agents ({agents.length})
            </h3>
            <button onClick={addAgent} className="btn-secondary text-xs py-2 px-3">
              <Plus className="w-3 h-3" />
              Add Agent
            </button>
          </div>
          <div className="space-y-4">
            {agents.map((agent, i) => (
              <div key={i} className="p-4 rounded-xl bg-[#1a1a24] border border-[#2a2a3a]">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-[#00d4ff]">Agent {i + 1}</span>
                  {agents.length > 1 && (
                    <button onClick={() => removeAgent(i)} className="p-1 hover:bg-[#ef4444]/20 rounded">
                      <Trash2 className="w-4 h-4 text-[#ef4444]" />
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <input className="input-field" placeholder="Name"
                    value={agent.name} onChange={e => {
                      const newAgents = [...agents]
                      newAgents[i].name = e.target.value
                      setAgents(newAgents)
                    }} />
                  <input className="input-field" placeholder="Role"
                    value={agent.role} onChange={e => {
                      const newAgents = [...agents]
                      newAgents[i].role = e.target.value
                      setAgents(newAgents)
                    }} />
                  <input className="input-field" placeholder="Goal"
                    value={agent.goal} onChange={e => {
                      const newAgents = [...agents]
                      newAgents[i].goal = e.target.value
                      setAgents(newAgents)
                    }} />
                  <select className="select-field"
                    value={agent.model} onChange={e => {
                      const newAgents = [...agents]
                      newAgents[i].model = e.target.value
                      setAgents(newAgents)
                    }}>
                    {models.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                  </select>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tasks */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-[#7c3aed]" />
              Tasks ({tasks.length})
            </h3>
            <button onClick={addTask} className="btn-secondary text-xs py-2 px-3">
              <Plus className="w-3 h-3" />
              Add Task
            </button>
          </div>
          <div className="space-y-4">
            {tasks.map((task, i) => (
              <div key={i} className="p-4 rounded-xl bg-[#1a1a24] border border-[#2a2a3a]">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-medium text-[#7c3aed]">Task {i + 1}</span>
                  {tasks.length > 1 && (
                    <button onClick={() => removeTask(i)} className="p-1 hover:bg-[#ef4444]/20 rounded">
                      <Trash2 className="w-4 h-4 text-[#ef4444]" />
                    </button>
                  )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <textarea className="textarea-field" placeholder="Task description..."
                    value={task.description} onChange={e => {
                      const newTasks = [...tasks]
                      newTasks[i].description = e.target.value
                      setTasks(newTasks)
                    }} />
                  <div className="space-y-3">
                    <input className="input-field" placeholder="Expected output"
                      value={task.expected_output} onChange={e => {
                        const newTasks = [...tasks]
                        newTasks[i].expected_output = e.target.value
                        setTasks(newTasks)
                      }} />
                    <select className="select-field"
                      value={task.agent_name} onChange={e => {
                        const newTasks = [...tasks]
                        newTasks[i].agent_name = e.target.value
                        setTasks(newTasks)
                      }}>
                      <option value="">Assign to agent...</option>
                      {agents.filter(a => a.name).map((a, idx) => (
                        <option key={idx} value={a.name}>{a.name}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <button onClick={handleSubmit} className="btn-primary w-full justify-center py-4 text-lg">
          <Play className="w-5 h-5" />
          Launch Crew
        </button>
      </div>
    </div>
  )
}

// ── Main App Component ──────────────────────────────────────────────────────

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-[#0a0a0f]">
      <Sidebar isOpen={sidebarOpen} setIsOpen={setSidebarOpen} />
      <div className="flex-1 flex flex-col min-w-0">
        <Header setSidebarOpen={setSidebarOpen} />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agents" element={<AgentsPage />} />
            <Route path="/crews" element={<CrewsPage />} />
            <Route path="/crews/create" element={<CreateCrewPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/skills" element={<SkillsPage />} />
            <Route path="/templates" element={<TemplatesPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
