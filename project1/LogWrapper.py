import sys,logging, os # pragma: no cover
from dotenv import load_dotenv # pragma: no cover
from logging.handlers import TimedRotatingFileHandler # pragma: no cover


class LogWrapper(object):
    """
    Implements a wrapper for the log library.
    https://www.datadoghq.com/blog/python-logging-best-practices/

    """

    logger = 0
    LEVEL = 1

    def __init__(self):
        # pass
        load_dotenv()
        # if (os.environ.get('LOG_LEVEL') == '1'):
        #     self.LEVEL = logging.INFO
        # elif (os.environ.get('LOG_LEVEL') == '2'):
        #     self.LEVEL = logging.DEBUG
        # else:
        #     self.LEVEL = logging.CRITICAL

    def set_logger(self, name):
        '''Creates a logger object for a class. Takes an argument "name"
            which is the name of the current file. This will allow the logging
            method to include the file name in the log message'''


        #: add error handling in here
        # print("hello")
        FORMAT = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
        # print("hello")
        # LOG_FILE = os.environ.get('LOG_FILE')
        # print(LOG_FILE)
        # Check to make sure that this doesnt throw an errror if it doesnt have absolute path to log directory

        # make handlers
        # file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
        # print("hello")
        # file_handler.setFormatter(FORMAT)
        # print("hello")

        #create logger object
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.LEVEL)
        # self.logger.addHandler(file_handler)
        self.logger.propagate = False

    # def critical(self, msg)->None:
    #     self.logger.critical(msg)

    def info(self, msg)->None:
        self.logger.info(msg)

    def debug(self, msg)->None:
        self.logger.debug(msg)

    def log_exception(self, method_name, msg=""):
        self.logger.error("Exception in —%s—, exception is —%s—. %s", method_name, \
            sys.exc_info()[0].__name__,  msg)
        # self.logger.critical("Error in %s, exception is %s.", method_name, \
            # exc_info=1)
        self.logger.debug("", exc_info=1)
        # self.logger.debug()



    def log_class_instantiation(self):
        '''Logs the state of the class right after instantiation.'''
        self.logger.debug(' Instantiated class with variable values %s', \
                            self.get_class_vars() )

    def log_method_call(self, method_name, *args):
        '''Logs the state of the class right after a method is called but before
        it is executed.'''
        args_str = ','.join(map(str,args))

        try:
            args_str.pop[0]
        except:
            args_str = "None"

        self.logger.debug('Method —%s— arguments —%s—', \
            method_name, args_str)

    def log_method_return(self, method_name, return_val="null"):
        '''Logs the state of the class and return value right after a method is
         executed. '''
        self.logger.info('Method —%s— return val —%s—',
                        method_name, return_val)
        # self.logger.debug('Returning from method —%s— with return value' + \
        #                 ' —%s—, class state after method executed is %s', \
        #                 method_name, "None", self.get_class_vars())

        '''Helper method that will return a string of all the current variables
        within a class.'''
    def get_class_vars(self):
        class_vars = vars(self).copy()
        class_vars.pop("logger", None)
        return str([*class_vars.items()])
        # return self

    def log_method_decorator(function):
        '''Decorator that will perform logging on a method.'''
        def _wrapper(*args):
            self = args[0]

            self.log_method_call(function.__name__, *args)
            retval = function(*args)
            self.log_method_return(function.__name__, retval)
            return retval
            # self.log_method_return(function.__name__, retval)
        return _wrapper

    def log_init_decorator(function):
        '''Decorator that will perform logging on class instantiations.'''
        def _wrapper(*args):
            self = args[0]
            #function(*args)
            self.log_class_instantiation()
        return _wrapper
