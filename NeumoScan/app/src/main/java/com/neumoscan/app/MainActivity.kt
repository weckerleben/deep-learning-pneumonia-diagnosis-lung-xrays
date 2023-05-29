package com.neumoscan.app

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.icu.text.SimpleDateFormat
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.widget.ImageView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import com.neumoscan.app.ui.theme.NeumoScanTheme
import java.io.File
import java.io.IOException
import java.util.Date
import java.util.Locale


class MainActivity : ComponentActivity() {
    private companion object {
        private const val REQUEST_IMAGE_CAPTURE = 1
        private const val REQUEST_CAMERA_PERMISSION = 2
        private const val CAMERA_PERMISSION_CODE = 100
        private const val PERMISSION_REQUEST_CODE = 1001
    }

    private val inputSize: Long = 224L
    private var currentPhotoPath: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            NeumoScanTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    Column(
                        modifier = Modifier.fillMaxSize(),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Greeting("Android")
                        Spacer(modifier = Modifier.height(16.dp))
                        TakePhotoButton(this@MainActivity)
                    }
                }
            }
        }
    }


    private fun checkAndRequestPermissions() {
        val permissionsToRequest = mutableListOf<String>()
        val cameraPermission = Manifest.permission.CAMERA
        val storagePermission = Manifest.permission.WRITE_EXTERNAL_STORAGE

        // Verifica el permiso de la cámara
        if (!isPermissionGranted(cameraPermission)) {
            permissionsToRequest.add(cameraPermission)
        }

        // Verifica el permiso de almacenamiento
        if (!isPermissionGranted(storagePermission)) {
            permissionsToRequest.add(storagePermission)
        }

        // Solicita los permisos necesarios
        if (permissionsToRequest.isNotEmpty()) {
            requestPermissions(permissionsToRequest.toTypedArray(), PERMISSION_REQUEST_CODE)
        } else {
            // Todos los permisos ya están otorgados, puedes proceder con la captura de la imagen
            dispatchTakePictureIntent()
        }
    }

    private fun isPermissionGranted(permission: String): Boolean {
        return ContextCompat.checkSelfPermission(this, permission) == PackageManager.PERMISSION_GRANTED
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<String>,
        grantResults: IntArray
    ) {
        if (requestCode == PERMISSION_REQUEST_CODE) {
            var allPermissionsGranted = true
            for (result in grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    allPermissionsGranted = false
                    break
                }
            }
            if (allPermissionsGranted) {
                // Los permisos fueron otorgados, puedes proceder con la captura de la imagen
                captureImage()
            } else {
                // Al menos uno de los permisos no fue otorgado, puedes mostrar un mensaje de error o tomar alguna otra acción
                Toast.makeText(this, "Se requieren permisos de cámara", Toast.LENGTH_SHORT).show()
            }
        } else {
            super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        }
    }

    private fun captureImage() {
        val takePictureIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        if (takePictureIntent.resolveActivity(packageManager) != null) {
            val photoFile: File? = try {
                createImageFile()
            } catch (ex: IOException) {
                // Maneja el error al crear el archivo
                ex.printStackTrace()
                null
            }
            // Continúa solo si el archivo se ha creado correctamente
            photoFile?.also {
                val photoURI: Uri = FileProvider.getUriForFile(
                    this,
                    "com.neumoscan.app.fileprovider",
                    it
                )
                // Guarda la ruta de la imagen para su posterior uso
                currentPhotoPath = photoFile.absolutePath
                // Configura la URI del archivo como extra en el intent de la cámara
                takePictureIntent.putExtra(MediaStore.EXTRA_OUTPUT, photoURI)
                startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE)
            }
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == Activity.RESULT_OK) {
            val imageView: ImageView = findViewById(R.id.imageView)
            imageView.setImageURI(Uri.parse(currentPhotoPath))
        }
    }

    @Composable
    fun Greeting(name: String) {
        Text(
            text = "Hello $name!",
            modifier = Modifier.padding(16.dp),
            color = Color.Transparent,
            fontWeight = FontWeight.Bold
        )
    }

    @Throws(IOException::class)
    private fun createImageFile(): File {
        // Crea un nombre único para el archivo de imagen
        val timeStamp: String = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val storageDir: File? = getExternalFilesDir(Environment.DIRECTORY_PICTURES)
        return File.createTempFile(
            "JPEG_${timeStamp}_", /* prefijo del archivo */
            ".jpg", /* extensión del archivo */
            storageDir /* directorio de almacenamiento */
        ).apply {
            // Guarda la ruta del archivo
            currentPhotoPath = absolutePath
        }
    }

    private fun dispatchTakePictureIntent() {
        checkAndRequestPermissions()
    }

    @Composable
    fun TakePhotoButton(activity: ComponentActivity) {
        Button(
            onClick = { dispatchTakePictureIntent() },
            modifier = Modifier.padding(16.dp)
        ) {
            Text(text = "Take Photo")
        }
    }

    @Preview(showBackground = true)
    @Composable
    fun DefaultPreview() {
        NeumoScanTheme {
            Column(
                modifier = Modifier.fillMaxSize(),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Greeting("Android")
                Spacer(modifier = Modifier.height(16.dp))
                TakePhotoButton(activity = ComponentActivity())
            }
        }
    }
}
