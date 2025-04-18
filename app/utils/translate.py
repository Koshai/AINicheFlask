import argostranslate.package
import argostranslate.translate
from flask import current_app

def translate_to_bangla(content):
    """Translate content from English to Bangla using argostranslate"""
    try:
        # Check if packages are installed
        installed_languages = argostranslate.translate.get_installed_languages()
        from_lang = next((lang for lang in installed_languages if lang.code == "en"), None)
        to_lang = next((lang for lang in installed_languages if lang.code == "bn"), None)

        if not from_lang or not to_lang:
            # Try to install required packages
            current_app.logger.info("Required language packages not found. Attempting to install...")
            try_install_language_packages()
            
            # Check again after installation
            installed_languages = argostranslate.translate.get_installed_languages()
            from_lang = next((lang for lang in installed_languages if lang.code == "en"), None)
            to_lang = next((lang for lang in installed_languages if lang.code == "bn"), None)
            
            if not from_lang or not to_lang:
                current_app.logger.error("Could not install required language packages")
                return content

        translation = from_lang.get_translation(to_lang)
        return translation.translate(content)
    except Exception as e:
        current_app.logger.error(f"Translation error: {str(e)}")
        return content

def try_install_language_packages():
    """Attempt to download and install en-bn translation packages"""
    try:
        # Update package index
        argostranslate.package.update_package_index()
        
        # Get available packages
        available_packages = argostranslate.package.get_available_packages()
        
        # Find the en-bn package
        en_bn_package = next(
            (pkg for pkg in available_packages if pkg.from_code == "en" and pkg.to_code == "bn"), 
            None
        )
        
        if en_bn_package:
            # Download and install
            argostranslate.package.install_from_path(en_bn_package.download())
            current_app.logger.info("Successfully installed en-bn translation package")
        else:
            current_app.logger.error("en-bn translation package not found in package index")
    except Exception as e:
        current_app.logger.error(f"Error installing language packages: {str(e)}")