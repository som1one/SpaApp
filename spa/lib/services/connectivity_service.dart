import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';

class ConnectivityService {
  final Connectivity _connectivity = Connectivity();
  StreamController<bool>? _connectivityController;
  StreamSubscription<List<ConnectivityResult>>? _subscription;

  Stream<bool> get connectivityStream {
    _connectivityController ??= StreamController<bool>.broadcast();
    return _connectivityController!.stream;
  }

  Future<bool> hasInternetConnection() async {
    try {
      final connectivityResults = await _connectivity.checkConnectivity();
      
      // Если нет подключения вообще
      if (connectivityResults.isEmpty || 
          connectivityResults.contains(ConnectivityResult.none)) {
        return false;
      }

      // Есть подключение (WiFi, mobile, ethernet и т.д.)
      return true;
    } catch (e) {
      // В случае ошибки предполагаем, что нет интернета
      return false;
    }
  }

  void startMonitoring() {
    _subscription?.cancel();
    _subscription = _connectivity.onConnectivityChanged.listen(
      (List<ConnectivityResult> results) {
        final hasConnection = results.isNotEmpty && 
            !results.contains(ConnectivityResult.none);
        _connectivityController?.add(hasConnection);
      },
    );
  }

  void stopMonitoring() {
    _subscription?.cancel();
    _subscription = null;
  }

  void dispose() {
    stopMonitoring();
    _connectivityController?.close();
    _connectivityController = null;
  }
}

