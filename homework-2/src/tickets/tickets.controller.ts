import {
  BadRequestException,
  Body,
  Controller,
  Delete,
  Get,
  HttpCode,
  HttpStatus,
  Param,
  Post,
  Put,
  Query,
  UploadedFile,
  UseInterceptors,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { extname } from 'node:path';
import { ImportFormat, SUPPORTED_IMPORT_FORMATS } from '../import/import-summary';
import { ImportService } from '../import/import.service';
import { CreateTicketDto } from './dto/create-ticket.dto';
import { QueryTicketsDto } from './dto/query-tickets.dto';
import { UpdateTicketDto } from './dto/update-ticket.dto';
import { TicketsService } from './tickets.service';

function isTruthyFlag(value: unknown): boolean {
  return value === true || value === 'true' || value === '1';
}

/** Infers the import format from an explicit query param, the filename, or the mimetype. */
function resolveImportFormat(
  file: Express.Multer.File,
  explicitFormat?: string,
): ImportFormat {
  const candidate = (explicitFormat ?? extname(file.originalname).slice(1)).toLowerCase();
  if ((SUPPORTED_IMPORT_FORMATS as string[]).includes(candidate)) {
    return candidate as ImportFormat;
  }

  if (file.mimetype.includes('json')) return 'json';
  if (file.mimetype.includes('xml')) return 'xml';
  if (file.mimetype.includes('csv')) return 'csv';

  throw new BadRequestException(
    `Could not determine import format from file "${file.originalname}". Provide ?format=csv|json|xml.`,
  );
}

@Controller('tickets')
export class TicketsController {
  constructor(
    private readonly ticketsService: TicketsService,
    private readonly importService: ImportService,
  ) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  create(@Body() dto: CreateTicketDto) {
    return this.ticketsService.create(dto);
  }

  @Post('import')
  @HttpCode(HttpStatus.OK)
  @UseInterceptors(FileInterceptor('file'))
  async importTickets(
    @UploadedFile() file: Express.Multer.File,
    @Query('format') format?: string,
    @Query('autoClassify') autoClassify?: string,
  ) {
    if (!file) {
      throw new BadRequestException('A file upload under the "file" field is required');
    }

    const resolvedFormat = resolveImportFormat(file, format);
    return this.importService.import(
      file.buffer.toString('utf-8'),
      resolvedFormat,
      isTruthyFlag(autoClassify),
    );
  }

  @Get()
  findAll(@Query() query: QueryTicketsDto) {
    return this.ticketsService.findAll(query);
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.ticketsService.findOne(id);
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() dto: UpdateTicketDto) {
    return this.ticketsService.update(id, dto);
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  remove(@Param('id') id: string) {
    this.ticketsService.remove(id);
  }

  @Post(':id/auto-classify')
  @HttpCode(HttpStatus.OK)
  autoClassify(@Param('id') id: string) {
    const ticket = this.ticketsService.autoClassify(id);
    return ticket.classification;
  }
}
