import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == '__main__':
    import argparse

    import pyipttool.cache
    import pyipttool.dump
    import pyipttool.ipt

    def auto_int(x):
        return int(x, 0)

    parser = argparse.ArgumentParser(description='pyipt')
    parser.add_argument('-c', action = "store", dest = "cache_file")
    parser.add_argument('-p', action = "store", default = "", dest = "pt_file")
    parser.add_argument('-d', action = "store", default = "", dest = "dump_file")
    parser.add_argument('-s', action = "store", dest = "symbol")
    parser.add_argument('-C', dest = "cr3", default = 0, type = auto_int)

    args = parser.parse_args()

    block_analyzer = pyipttool.cache.Reader(args.cache_file, args.pt_file)

    dump_loader = pyipttool.dump.Loader(args.dump_file)
    if args.symbol:
        address = dump_loader.resolve_symbol_address(args.symbol)

        for (sync_offset, offset) in block_analyzer.enumerate_blocks(address, cr3 = args.cr3):
            print('> sync_offset = %x / offset = %x' % (sync_offset, offset))

            pt_log_analyzer = pyipttool.ipt.Analyzer(args.dump_file, dump_symbols = True, load_image = True)
            pt_log_analyzer.open_ipt_log(args.pt_file, start_offset = sync_offset, end_offset = offset+2)
            for insn in pt_log_analyzer.enumerate_instructions(move_forward = False, instruction_offset = offset):
                disasmline = dump_loader.get_disassembly_line(insn.ip)
                print('\tInstruction: %s' % (disasmline))
