import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'dart:convert';
import 'dart:async';

void main() {
  runApp(const JarvisApp());
}

class JarvisApp extends StatelessWidget {
  const JarvisApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'J.A.R.V.I.S.',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        primaryColor: const Color(0xFF00D9FF),
        scaffoldBackgroundColor: const Color(0xFF0A0A0F),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00D9FF),
          secondary: Color(0xFF00FF88),
          surface: Color(0xFF1A1A2E),
        ),
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  
  final String apiUrl = 'http://192.168.1.100:8000'; // CAMBIA ESTA IP
  
  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }
  
  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              const Color(0xFF0A0A0F),
              const Color(0xFF0F1923),
              const Color(0xFF0A0A0F),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  border: Border(
                    bottom: BorderSide(
                      color: const Color(0xFF00D9FF).withOpacity(0.2),
                      width: 1,
                    ),
                  ),
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.smart_toy_outlined,
                      color: Color(0xFF00D9FF),
                      size: 28,
                    ),
                    const SizedBox(width: 12),
                    const Text(
                      'J.A.R.V.I.S.',
                      style: TextStyle(
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF00D9FF),
                        letterSpacing: 2,
                      ),
                    ),
                    const Spacer(),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFF00FF88).withOpacity(0.2),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF00FF88).withOpacity(0.5)),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.circle, size: 8, color: Color(0xFF00FF88)),
                          SizedBox(width: 6),
                          Text(
                            'ONLINE',
                            style: TextStyle(
                              fontSize: 10,
                              color: Color(0xFF00FF88),
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              
              // Tabs
              TabBar(
                controller: _tabController,
                labelColor: const Color(0xFF00D9FF),
                unselectedLabelColor: Colors.grey,
                indicatorColor: const Color(0xFF00D9FF),
                tabs: const [
                  Tab(icon: Icon(Icons.chat), text: 'Chat'),
                  Tab(icon: Icon(Icons.dashboard), text: 'Sistema'),
                  Tab(icon: Icon(Icons.security), text: 'Seguridad'),
                  Tab(icon: Icon(Icons.build), text: 'Iron Man'),
                ],
              ),
              
              // Tab Views
              Expanded(
                child: TabBarView(
                  controller: _tabController,
                  children: [
                    ChatTab(apiUrl: apiUrl),
                    SystemTab(apiUrl: apiUrl),
                    SecurityTab(apiUrl: apiUrl),
                    IronManTab(apiUrl: apiUrl),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ==================== CHAT TAB ====================

class ChatTab extends StatefulWidget {
  final String apiUrl;
  const ChatTab({super.key, required this.apiUrl});

  @override
  State<ChatTab> createState() => _ChatTabState();
}

class _ChatTabState extends State<ChatTab> {
  final TextEditingController _controller = TextEditingController();
  final List<Map<String, String>> _messages = [];
  bool _isTyping = false;
  
  final stt.SpeechToText _speech = stt.SpeechToText();
  final FlutterTts _tts = FlutterTts();
  bool _isListening = false;

  @override
  void initState() {
    super.initState();
    _initTts();
    _messages.add({
      'role': 'ai',
      'content': '¡Hola! Soy J.A.R.V.I.S., tu asistente de IA. ¿En qué puedo ayudarte? 🤖'
    });
  }
  
  Future<void> _initTts() async {
    await _tts.setLanguage('es-ES');
    await _tts.setPitch(1.0);
    await _tts.setSpeechRate(0.5);
  }

  Future<void> _sendMessage() async {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    
    setState(() {
      _messages.add({'role': 'user', 'content': text});
      _isTyping = true;
    });
    _controller.clear();
    
    try {
      final response = await http.post(
        Uri.parse('${widget.apiUrl}/brain/command'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'command': text,
          'interface': 'app',
          'user_id': 8406954800
        }),
      );
      
      final data = json.decode(response.body);
      
      setState(() {
        _messages.add({'role': 'ai', 'content': data['response'] ?? 'Sin respuesta'});
        _isTyping = false;
      });
      
      // Speak response
      _tts.speak(data['response'] ?? '');
      
    } catch (e) {
      setState(() {
        _messages.add({'role': 'ai', 'content': '❌ Error: $e'});
        _isTyping = false;
      });
    }
  }
  
  Future<void> _startListening() async {
    if (!_isListening) {
      bool available = await _speech.initialize();
      if (available) {
        setState(() => _isListening = true);
        _speech.listen(
          onResult: (result) {
            _controller.text = result.recognizedWords;
          },
          localeId: 'es_ES',
        );
      }
    } else {
      _speech.stop();
      setState(() => _isListening = false);
      if (_controller.text.isNotEmpty) {
        _sendMessage();
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // Messages
        Expanded(
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: _messages.length + (_isTyping ? 1 : 0),
            itemBuilder: (context, index) {
              if (index == _messages.length) {
                return _buildTypingIndicator();
              }
              return _buildMessage(_messages[index]);
            },
          ),
        ),
        
        // Quick Actions
        Container(
          height: 60,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              _quickChip('🔋 Batería', 'batería'),
              _quickChip('📊 Sistema', 'diagnóstico'),
              _quickChip('🛡️ Seguridad', 'seguridad'),
              _quickChip('🎯 Táctico', 'análisis táctico'),
              _quickChip('🔧 Taller', 'taller'),
            ],
          ),
        ),
        
        // Input
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.3),
            border: Border(
              top: BorderSide(
                color: const Color(0xFF00D9FF).withOpacity(0.2),
                width: 1,
              ),
            ),
          ),
          child: Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _controller,
                  decoration: InputDecoration(
                    hintText: 'Mensaje para J.A.R.V.I.S...',
                    hintStyle: TextStyle(color: Colors.grey[600]),
                    filled: true,
                    fillColor: Colors.white.withOpacity(0.05),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(24),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 12,
                    ),
                  ),
                  onSubmitted: (_) => _sendMessage(),
                ),
              ),
              const SizedBox(width: 8),
              GestureDetector(
                onTap: _startListening,
                child: Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      colors: _isListening
                          ? [const Color(0xFFFF4444), const Color(0xFFFF6666)]
                          : [const Color(0xFF00D9FF), const Color(0xFF00FF88)],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: (_isListening ? const Color(0xFFFF4444) : const Color(0xFF00D9FF))
                            .withOpacity(0.5),
                        blurRadius: 12,
                        spreadRadius: 2,
                      ),
                    ],
                  ),
                  child: Icon(
                    _isListening ? Icons.stop : Icons.mic,
                    color: Colors.white,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: const LinearGradient(
                    colors: [Color(0xFF00D9FF), Color(0xFF00FF88)],
                  ),
                ),
                child: IconButton(
                  icon: const Icon(Icons.send, color: Colors.white),
                  onPressed: _sendMessage,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
  
  Widget _buildMessage(Map<String, String> msg) {
    final isUser = msg['role'] == 'user';
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.8),
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: isUser
              ? const Color(0xFF00D9FF).withOpacity(0.2)
              : Colors.white.withOpacity(0.05),
          borderRadius: BorderRadius.circular(16).copyWith(
            bottomRight: isUser ? const Radius.circular(4) : null,
            bottomLeft: !isUser ? const Radius.circular(4) : null,
          ),
          border: Border.all(
            color: isUser
                ? const Color(0xFF00D9FF).withOpacity(0.3)
                : Colors.white.withOpacity(0.1),
          ),
        ),
        child: Text(
          msg['content'] ?? '',
          style: const TextStyle(fontSize: 15, height: 1.5),
        ),
      ),
    );
  }
  
  Widget _buildTypingIndicator() {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _typingDot(0),
          _typingDot(200),
          _typingDot(400),
        ],
      ),
    );
  }
  
  Widget _typingDot(int delayMs) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0, end: 1),
      duration: const Duration(milliseconds: 600),
      builder: (context, value, child) {
        return Container(
          margin: const EdgeInsets.symmetric(horizontal: 3),
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: const Color(0xFF00D9FF).withOpacity(value * 0.8),
          ),
        );
      },
    );
  }
  
  Widget _quickChip(String icon, String command) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: ActionChip(
        label: Text(icon),
        onPressed: () {
          _controller.text = command;
          _sendMessage();
        },
        backgroundColor: Colors.white.withOpacity(0.05),
        side: BorderSide(color: const Color(0xFF00D9FF).withOpacity(0.3)),
      ),
    );
  }
}

// ==================== SYSTEM TAB ====================

class SystemTab extends StatefulWidget {
  final String apiUrl;
  const SystemTab({super.key, required this.apiUrl});

  @override
  State<SystemTab> createState() => _SystemTabState();
}

class _SystemTabState extends State<SystemTab> {
  Map<String, dynamic> _status = {};
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadStatus();
  }
  
  Future<void> _loadStatus() async {
    try {
      final response = await http.get(Uri.parse('${widget.apiUrl}/brain/status'));
      setState(() {
        _status = json.decode(response.body);
        _loading = false;
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF00D9FF)));
    }
    
    return RefreshIndicator(
      onRefresh: _loadStatus,
      color: const Color(0xFF00D9FF),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _buildStatusCard('🧠', 'Clientes', '${_status['connected_clients'] ?? 0}'),
          _buildStatusCard('📊', 'Comandos', '${_status['total_commands'] ?? 0}'),
          _buildStatusCard('🔌', 'Plugins', '${_status['plugins']?['loaded_plugins'] ?? 0}'),
          
          const SizedBox(height: 24),
          const Text(
            'Memoria',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF00D9FF)),
          ),
          const SizedBox(height: 12),
          if (_status['memory'] != null) ...[
            _buildInfoRow('Memorias', '${_status['memory']['long_term_count'] ?? 0}'),
            _buildInfoRow('Conversaciones', '${_status['memory']['conversation_count'] ?? 0}'),
            _buildInfoRow('Preferencias', '${_status['memory']['preferences_count'] ?? 0}'),
          ],
          
          const SizedBox(height: 24),
          const Text(
            'Aprendizaje',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF00D9FF)),
          ),
          const SizedBox(height: 12),
          if (_status['learning'] != null) ...[
            _buildInfoRow('Tasa de éxito', '${((_status['learning']['success_rate'] ?? 0) * 100).toStringAsFixed(0)}%'),
            _buildInfoRow('Patrones', '${_status['learning']['learned_patterns'] ?? 0}'),
          ],
        ],
      ),
    );
  }
  
  Widget _buildStatusCard(String icon, String label, String value) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF00D9FF).withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Text(icon, style: const TextStyle(fontSize: 32)),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: TextStyle(color: Colors.grey[400], fontSize: 12)),
                Text(value, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF00D9FF))),
              ],
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey[400])),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}

// ==================== SECURITY TAB ====================

class SecurityTab extends StatefulWidget {
  final String apiUrl;
  const SecurityTab({super.key, required this.apiUrl});

  @override
  State<SecurityTab> createState() => _SecurityTabState();
}

class _SecurityTabState extends State<SecurityTab> {
  String _result = 'Presiona el botón para escanear';
  bool _scanning = false;

  Future<void> _scanSecurity() async {
    setState(() {
      _scanning = true;
      _result = 'Escaneando...';
    });
    
    try {
      final response = await http.post(
        Uri.parse('${widget.apiUrl}/brain/command'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'command': 'seguridad',
          'interface': 'app',
        }),
      );
      
      final data = json.decode(response.body);
      setState(() {
        _result = data['response'] ?? 'Sin resultado';
        _scanning = false;
      });
    } catch (e) {
      setState(() {
        _result = 'Error: $e';
        _scanning = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.05),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF00D9FF).withOpacity(0.2)),
          ),
          child: Column(
            children: [
              const Icon(Icons.security, size: 64, color: Color(0xFF00D9FF)),
              const SizedBox(height: 16),
              const Text(
                'Escaneo de Seguridad',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Text(
                'Escanea la red en busca de amenazas',
                style: TextStyle(color: Colors.grey[400]),
              ),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: _scanning ? null : _scanSecurity,
                  icon: _scanning
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : const Icon(Icons.shield),
                  label: Text(_scanning ? 'Escaneando...' : 'Iniciar Escaneo'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF00D9FF),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                ),
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 24),
        const Text(
          'Resultado',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF00D9FF)),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.3),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            _result,
            style: const TextStyle(fontSize: 14, height: 1.5),
          ),
        ),
      ],
    );
  }
}

// ==================== IRON MAN TAB ====================

class IronManTab extends StatefulWidget {
  final String apiUrl;
  const IronManTab({super.key, required this.apiUrl});

  @override
  State<IronManTab> createState() => _IronManTabState();
}

class _IronManTabState extends State<IronManTab> {
  String _result = 'Selecciona un protocolo';
  bool _loading = false;

  Future<void> _runProtocol(String command) async {
    setState(() {
      _loading = true;
      _result = 'Ejecutando protocolo...';
    });
    
    try {
      final response = await http.post(
        Uri.parse('${widget.apiUrl}/brain/command'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'command': command,
          'interface': 'app',
        }),
      );
      
      final data = json.decode(response.body);
      setState(() {
        _result = data['response'] ?? 'Sin resultado';
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _result = 'Error: $e';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Protocol Grid
        GridView.count(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          crossAxisCount: 2,
          mainAxisSpacing: 12,
          crossAxisSpacing: 12,
          childAspectRatio: 1.2,
          children: [
            _protocolCard('🔧', 'Diagnóstico', 'diagnóstico'),
            _protocolCard('🛡️', 'Seguridad', 'seguridad'),
            _protocolCard('🎯', 'Táctico', 'análisis táctico'),
            _protocolCard('📁', 'Taller', 'taller'),
            _protocolCard('💾', 'Backup', 'crear backup'),
            _protocolCard('🔋', 'Batería', 'batería'),
          ],
        ),
        
        const SizedBox(height: 24),
        const Text(
          'Resultado',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF00D9FF)),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.black.withOpacity(0.3),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF00D9FF).withOpacity(0.2)),
          ),
          child: _loading
              ? const Center(
                  child: CircularProgressIndicator(color: Color(0xFF00D9FF)),
                )
              : Text(
                  _result,
                  style: const TextStyle(fontSize: 14, height: 1.5),
                ),
        ),
      ],
    );
  }
  
  Widget _protocolCard(String icon, String name, String command) {
    return GestureDetector(
      onTap: () => _runProtocol(command),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.05),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFF00D9FF).withOpacity(0.3)),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(icon, style: const TextStyle(fontSize: 36)),
            const SizedBox(height: 8),
            Text(
              name,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.bold),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
