import 'dart:async';
import 'package:flutter/material.dart';
import '../services/connectivity_service.dart';
import 'offline_widget.dart';

class ConnectivityWrapper extends StatefulWidget {
  final Widget child;
  final VoidCallback? onRetry;
  final bool checkOnInit;

  const ConnectivityWrapper({
    super.key,
    required this.child,
    this.onRetry,
    this.checkOnInit = true,
  });

  @override
  State<ConnectivityWrapper> createState() => _ConnectivityWrapperState();
}

class _ConnectivityWrapperState extends State<ConnectivityWrapper> {
  final ConnectivityService _connectivityService = ConnectivityService();
  bool _hasInternet = true;
  bool _isChecking = false;
  StreamSubscription<bool>? _connectivitySubscription;

  @override
  void initState() {
    super.initState();
    if (widget.checkOnInit) {
      _checkConnectivity();
    }
    _connectivityService.startMonitoring();
    _connectivitySubscription = _connectivityService.connectivityStream.listen(
      (hasConnection) {
        if (mounted) {
          setState(() {
            _hasInternet = hasConnection;
          });
        }
      },
    );
  }

  Future<void> _checkConnectivity() async {
    setState(() {
      _isChecking = true;
    });
    final hasConnection = await _connectivityService.hasInternetConnection();
    if (mounted) {
      setState(() {
        _hasInternet = hasConnection;
        _isChecking = false;
      });
    }
  }

  Future<void> _retry() async {
    await _checkConnectivity();
    if (_hasInternet && widget.onRetry != null) {
      widget.onRetry!();
    }
  }

  @override
  void dispose() {
    _connectivitySubscription?.cancel();
    _connectivityService.stopMonitoring();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isChecking) {
      return Scaffold(
        backgroundColor: const Color(0xFFF7F7F2),
        body: const Center(
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (!_hasInternet) {
      return Scaffold(
        backgroundColor: const Color(0xFFF7F7F2),
        body: OfflineWidget(onRetry: _retry),
      );
    }

    return widget.child;
  }
}

