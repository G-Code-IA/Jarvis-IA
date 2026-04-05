import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'dart:convert';
import 'dart:async';

void main() {
  runApp(const JarvisSiriApp());
}

class JarvisSiriApp extends StatelessWidget {
  const JarvisSiriApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'J.A.R.V.I.S. Siri Mode',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        primaryColor: const Color(0xFF00D9FF),
        scaffoldBackgroundColor: const Color(0xFF000000),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF00D9FF),
          secondary: Color(0xFF00FF88),
          surface: Color(0xFF1A1A2E),
        ),
      ),
      home: const SiriHomePage(),
    );
  }
}

class SiriHomePage extends StatefulWidget {
  const SiriHomePage({super.key});

  @override
  State<SiriHomePage> createState() => _SiriHomePageState();
}

class _SiriHomePageState extends State<SiriHomePage>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _pulseAnimation;
  
  SpeechToText speech = stt.SpeechToText();
  FlutterTts tts = FlutterTts();
  
  bool isListening = false;
  bool isSpeaking = false;
  bool isProcessing = false;
  String currentText = "Toca el micrófono o di 'Hey JARVIS'";
  String responseText = "";
  
  String apiUrl = 'http://192.168.1.100:8000'; // CAMBIA ESTO
  Timer? _voiceActivationTimer;
  
  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.2).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );
    
    _initSpeech();
    _initTts();
    _startVoiceActivation();
  }
  
  Future<void> _initSpeech() async {
    await speech.initialize(
      onError: (error) => print('Error: $error'),
      onStatus: (status) {
        if (status == 'done' || status == 'notListening') {
          setState(() => isListening = false);
        }
      },
    );
  }
  
  Future<void> _initTts() async {
    await tts.setLanguage('es-ES');
    await tts.setPitch(1.0);
    await tts.setSpeechRate(0.5);
    
    tts.setCompletionHandler(() {
      setState(() => isSpeaking = false);
    });
  }
  
  void _startVoiceActivation() {
    // Escuchar continuamente "Hey JARVIS"
    _voiceActivationTimer = Timer.periodic(const Duration(seconds: 3), (timer) {
      if (!isListening && !isProcessing && !isSpeaking) {
        _startListening();
      }
    });
  }
  
  Future<void> _startListening() async {
    if (!await speech.isNotListening()) {
      return;
    }
    
    setState(() {
      isListening = true;
      currentText = "Escuchando...";
    });
    
    _animationController.repeat(reverse: true);
    
    await speech.listen(
      onResult: (result) {
        final recognized = result.recognizedWords.toLowerCase();
        print('Reconocido: $recognized');
        
        // Activación por voz
        if (recognized.contains('hey jarvis') || 
            recognized.contains('jarvis') ||
            recognized.contains('ok jarvis')) {
          
          // Continuar escuchando el comando
          _processVoiceCommand(recognized);
        }
      },
      localeId: 'es_ES',
      listenFor: const Duration(seconds: 5),
      pauseFor: const Duration(seconds: 2),
      partialResults: true,
      cancelOnError: true,
      listenMode: stt.ListenMode.confirmation,
    );
  }
  
  Future<void> _processVoiceCommand(String command) async {
    setState(() {
      isListening = false;
      isProcessing = true;
      currentText = command;
    });
    
    _animationController.stop();
    
    // Limpiar comando de activación
    command = command
        .replaceAll('hey jarvis', '')
        .replaceAll('ok jarvis', '')
        .replaceAll('jarvis', '')
        .trim();
    
    if (command.isEmpty) {
      command = "¿Qué puedo hacer por ti?";
    }
    
    try {
      // Enviar a API
      final response = await http.post(
        Uri.parse('$apiUrl/api/command'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'command': command}),
      );
      
      final data = json.decode(response.body);
      final responseText = data['response'] ?? 'No entendí eso';
      
      setState(() {
        this.responseText = responseText;
        currentText = responseText;
        isProcessing = false;
      });
      
      // Hablar respuesta
      _speak(responseText);
      
    } catch (e) {
      setState(() {
        isProcessing = false;
        currentText = 'Error de conexión';
      });
      _speak('Error de conexión. Verifica la API.');
    }
  }
  
  Future<void> _speak(String text) async {
    setState(() => isSpeaking = true);
    
    // Limpiar texto para TTS
    text = text
        .replaceAll(RegExp(r'[`*_#]'), '')
        .replaceAll(RegExp(r'\*\*'), '')
        .replaceAll('✅', '')
        .replaceAll('❌', '')
        .replaceAll('🔍', '')
        .replaceAll('📊', '')
        .trim();
    
    await tts.speak(text);
  }
  
  void _stopListening() {
    speech.stop();
    setState(() => isListening = false);
    _animationController.stop();
  }
  
  @override
  void dispose() {
    _voiceActivationTimer?.cancel();
    _animationController.dispose();
    speech.stop();
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Color(0xFF000000),
              Color(0xFF0A0A1A),
              Color(0xFF001A1A),
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Header
              Padding(
                padding: const EdgeInsets.all(20),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      '🤖 J.A.R.V.I.S.',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF00D9FF),
                      ),
                    ),
                    Row(
                      children: [
                        _buildStatusIcon('🎤', isListening),
                        const SizedBox(width: 10),
                        _buildStatusIcon('⚙️', isProcessing),
                        const SizedBox(width: 10),
                        _buildStatusIcon('🔊', isSpeaking),
                      ],
                    ),
                  ],
                ),
              ),
              
              // Animated Orb
              Expanded(
                child: Center(
                  child: AnimatedBuilder(
                    animation: _pulseAnimation,
                    builder: (context, child) {
                      return Transform.scale(
                        scale: _pulseAnimation.value,
                        child: Container(
                          width: 250,
                          height: 250,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            gradient: RadialGradient(
                              colors: isListening
                                  ? [
                                      const Color(0xFF00D9FF).withOpacity(0.8),
                                      const Color(0xFF00D9FF).withOpacity(0.4),
                                      Colors.transparent,
                                    ]
                                  : isProcessing
                                      ? [
                                          const Color(0xFFFFD700).withOpacity(0.8),
                                          const Color(0xFFFFD700).withOpacity(0.4),
                                          Colors.transparent,
                                        ]
                                      : isSpeaking
                                          ? [
                                              const Color(0xFF00FF88).withOpacity(0.8),
                                              const Color(0xFF00FF88).withOpacity(0.4),
                                              Colors.transparent,
                                            ]
                                          : [
                                              const Color(0xFF00D9FF).withOpacity(0.3),
                                              const Color(0xFF00D9FF).withOpacity(0.1),
                                              Colors.transparent,
                                            ],
                              stops: const [0.4, 0.7, 1.0],
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: isListening
                                    ? const Color(0xFF00D9FF).withOpacity(0.5)
                                    : isProcessing
                                        ? const Color(0xFFFFD700).withOpacity(0.5)
                                        : isSpeaking
                                            ? const Color(0xFF00FF88).withOpacity(0.5)
                                            : Colors.transparent,
                                blurRadius: isListening || isSpeaking ? 60 : 30,
                                spreadRadius: isListening || isSpeaking ? 20 : 10,
                              ),
                            ],
                          ),
                          child: Center(
                            child: Icon(
                              isListening
                                  ? Icons.mic
                                  : isProcessing
                                      ? Icons.psychology
                                      : isSpeaking
                                          ? Icons.volume_up
                                          : Icons.mic_none,
                              size: 80,
                              color: isListening
                                  ? const Color(0xFF00D9FF)
                                  : isProcessing
                                      ? const Color(0xFFFFD700)
                                      : isSpeaking
                                          ? const Color(0xFF00FF88)
                                          : Colors.white54,
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),
              
              // Current Text
              Padding(
                padding: const EdgeInsets.all(30),
                child: Text(
                  currentText,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 18,
                    color: Colors.white.withOpacity(0.8),
                    height: 1.5,
                  ),
                ),
              ),
              
              // Response Text
              if (responseText.isNotEmpty && responseText != currentText)
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 30),
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: const Color(0xFF00D9FF).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(15),
                    border: Border.all(
                      color: const Color(0xFF00D9FF).withOpacity(0.3),
                    ),
                  ),
                  child: Text(
                    responseText,
                    style: const TextStyle(
                      fontSize: 16,
                      color: Color(0xFF00D9FF),
                    ),
                  ),
                ),
              
              const SizedBox(height: 30),
              
              // Manual Mic Button
              GestureDetector(
                onTapDown: (_) => _startListening(),
                onTapUp: (_) => _stopListening(),
                onTapCancel: () => _stopListening(),
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    gradient: LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [
                        const Color(0xFF00D9FF),
                        const Color(0xFF00FF88),
                      ],
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF00D9FF).withOpacity(0.5),
                        blurRadius: 20,
                        spreadRadius: 5,
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.mic,
                    size: 40,
                    color: Colors.black,
                  ),
                ),
              ),
              
              const SizedBox(height: 30),
              
              // Quick Commands
              Wrap(
                spacing: 10,
                runSpacing: 10,
                alignment: WrapAlignment.center,
                children: [
                  _buildQuickCommand('🔋 Batería', 'batería'),
                  _buildQuickCommand('🌤️ Clima', 'clima en Madrid'),
                  _buildQuickCommand('📊 Sistema', 'sistema'),
                  _buildQuickCommand('🧠 Memoria', 'memoria'),
                  _buildQuickCommand('🔌 Plugins', 'plugins'),
                  _buildQuickCommand('📷 Foto', 'toma una foto'),
                ],
              ),
              
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
  
  Widget _buildStatusIcon(String icon, bool isActive) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: isActive
            ? const Color(0xFF00FF88).withOpacity(0.3)
            : Colors.white.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        icon,
        style: TextStyle(
          fontSize: 20,
          color: isActive ? const Color(0xFF00FF88) : Colors.white54,
        ),
      ),
    );
  }
  
  Widget _buildQuickCommand(String label, String command) {
    return Material(
      color: Colors.white.withOpacity(0.1),
      borderRadius: BorderRadius.circular(20),
      child: InkWell(
        borderRadius: BorderRadius.circular(20),
        onTap: () => _processVoiceCommand(command),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          child: Text(
            label,
            style: const TextStyle(
              fontSize: 14,
              color: Color(0xFF00D9FF),
            ),
          ),
        ),
      ),
    );
  }
}
